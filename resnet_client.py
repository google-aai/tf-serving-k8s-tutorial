#!/usr/bin/env python2.7
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A client that talks to tensorflow_model_server loaded with an image model.

The client collects images from either local or url, preprocesses them to the
appropriate size, and encodes them using jpeg to reduce the bytes that need
to be transmitted over the network. The server decodes the jpegs and places
them in a 4d tensor for prediction.
"""

from __future__ import print_function

import argparse
import csv
import json
import time
import urllib

import cv2
from grpc.beta import implementations
import numpy as np
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2
from google.protobuf import json_format


def resize_and_pad_image(img, output_image_dim=128):
  """Resize the image to make it IMAGE_DIM x IMAGE_DIM pixels in size.

  If an image is not square, it will pad the top/bottom or left/right
  with black pixels to ensure the image is square.

  Args:
    img: the input 3-color image
    output_image_dim: resized and padded output length (and width)

  Returns:
    resized and padded image
  """

  h, w = img.shape[:2]

  # interpolation method
  if h > output_image_dim or w > output_image_dim:
    # use preferred interpolation method for shrinking image
    interp = cv2.INTER_AREA
  else:
    # use preferred interpolation method for stretching image
    interp = cv2.INTER_CUBIC

  # aspect ratio of image
  aspect = float(w) / h

  # compute scaling and pad sizing
  if aspect > 1:  # Image is "wide". Add black pixels on top and bottom.
    new_w = output_image_dim
    new_h = np.round(new_w / aspect)
    pad_vert = (output_image_dim - new_h) / 2
    pad_top, pad_bot = int(np.floor(pad_vert)), int(np.ceil(pad_vert))
    pad_left, pad_right = 0, 0
  elif aspect < 1:  # Image is "tall". Add black pixels on left and right.
    new_h = output_image_dim
    new_w = np.round(new_h * aspect)
    pad_horz = (output_image_dim - new_w) / 2
    pad_left, pad_right = int(np.floor(pad_horz)), int(np.ceil(pad_horz))
    pad_top, pad_bot = 0, 0
  else:  # square image
    new_h = output_image_dim
    new_w = output_image_dim
    pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0

  # scale to IMAGE_DIM x IMAGE_DIM and pad with zeros (black pixels)
  scaled_img = cv2.resize(img, (int(new_w), int(new_h)), interpolation=interp)
  scaled_img = cv2.copyMakeBorder(scaled_img,
                                  pad_top, pad_bot, pad_left, pad_right,
                                  borderType=cv2.BORDER_CONSTANT, value=0)
  return scaled_img


def main():
  # Command line arguments
  parser = argparse.ArgumentParser('Label an image using the cat model')
  parser.add_argument(
      '-s',
      '--server',
      help='URL of host serving the cat model'
  )
  parser.add_argument(
      '-p',
      '--port',
      type=int,
      default=9000,
      help='Port at which cat model is being served'
  )
  parser.add_argument(
      '-m',
      '--model',
      type=str,
      default='resnet',
      help='Paths (local or url) to images you would like to label'
  )
  parser.add_argument(
      '-d',
      '--dim',
      type=int,
      default=224,
      help='Size of (square) image, an integer indicating its width and '
           'height. Resnet\'s default is 224'
  )
  parser.add_argument(
      '--profile_only',
      action='store_true',
      default=False,
      help='False means print the classification and score results of the '
           'batch. True if you are simply profiling your model speed.'
  )
  parser.add_argument(
      '-r',
      '--replicate_samples_power',
      type=int,
      default=0,
      help='This flag is primarily for profiling batch predictions. '
           'Creates 2^r copies of the specified images, and sends them to '
           'the server.'
  )
  parser.add_argument(
      'images',
      type=str,
      nargs='+',
      help='Paths (local, GCS, or url) to images you would like to label'
  )

  args = parser.parse_args()
  host = args.server
  port = args.port

  # Preprocess images at the client and compress as jpeg
  img_size = args.dim
  images = args.images
  png_array = []

  for image in images:
    feature = None
    if 'http' in image:
      resp = urllib.urlopen(image)
      feature = np.asarray(bytearray(resp.read()), dtype='uint8')
      feature = cv2.imdecode(feature, cv2.IMREAD_COLOR)
    else:
      feature = cv2.imread(image)  # Parse the image from your local disk.
    # Resize and pad the image
    feature = resize_and_pad_image(feature, output_image_dim=int(img_size))
    # Append to features_array
    png_image = cv2.imencode('.jpg', feature)[1].tostring()
    png_array.append(png_image)

  # Things that you need ot do to send an RPC request to the TF server.
  channel = implementations.insecure_channel(host, int(port))
  stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
  # Create a prediction request to send to the server
  request = predict_pb2.PredictRequest()
  # Call 'resnet' model to make prediction on the image
  request.model_spec.name = args.model

  # Option: create 2^r copies of the array for profiling.
  for i in range(0, args.replicate_samples_power):
    png_array = np.append(png_array, png_array, axis=0)

  request.inputs['images'].CopyFrom(
      tf.contrib.util.make_tensor_proto(
          png_array,
          shape=[len(png_array)],
          dtype=tf.string
      )
  )

  start_time = int(round(time.time() * 1000))
  # Call the server to predict, and return the result
  result = stub.Predict(request, 1800.0)  # 5 minute timeout
  # Stop the timer and write to log
  elapsed = int(round(time.time() * 1000)) - start_time

  print('Request delay: ' + str(elapsed) + ' ms')

  # If you're not running profile_only mode, pretty-print the results.
  if not args.profile_only:
    json_result = json.loads(json_format.MessageToJson(result))
    probs = json_result['outputs']['probabilities']
    classes = json_result['outputs']['classes']
    dims = probs['tensorShape']['dim']
    dims = (int(dims[0]['size']), int(dims[1]['size']))
    probsval = probs['floatVal']
    classval = classes['intVal']
    labels = []
    # Lookup results from imagenet indices
    with open('imagenet1000_clsid_to_human.txt', 'r') as f:
      label_reader = csv.reader(f, delimiter=':', quotechar='\'')
      for row in label_reader:
        labels.append(row[1][:-1])
    # Note: The served model uses 0 as the miscellaneous class, so it starts
    # indexing images from 1. Subtract 1 to reference the dict file correctly.
    classval = [labels[x - 1] for x in classval]
    class_and_probs = [str(p) + ' : ' + c for c, p in zip(classval, probsval)]
    class_and_probs = np.reshape(class_and_probs, dims)
    for i in range(0, len(images)):
      print('Image: ' + images[i])
      for j in range(0, 5):
        print(class_and_probs[i][j])


if __name__ == '__main__':
  main()
