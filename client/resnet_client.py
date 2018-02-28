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

from grpc.beta import implementations
import numpy as np
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2
from google.protobuf import json_format

from image_processing import preprocess_and_encode_images

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
      '-t',
      '--model_type',
      type=str,
      default='estimator',
      help='Model implementation type.'
           'Default is \'estimator\'. Other options: \'keras\''
  )
  parser.add_argument(
      'images',
      type=str,
      nargs='+',
      help='Paths (local, GCS, or url) to images you would like to label'
  )

  args = parser.parse_args()
  images = args.images

  # Convert image paths/urls to a batch of jpegs
  jpeg_batch = preprocess_and_encode_images(images, args.dim)

  # Call the server to predict top 5 classes and probabilities, and time taken
  result, elapsed = predict_and_profile(
      args.server, args.port, args.model, jpeg_batch)

  # Parse server message and print formatted results
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
  if args.model_type.lower() == 'estimator':
    classval = [labels[x - 1] for x in classval]
  elif args.model_type.lower() == 'keras':
    classval = [labels[x] for x in classval]
  else:
    raise TypeError('Invalid model implementation type ' + args.model_type)
  class_and_probs = [str(p) + ' : ' + c for c, p in zip(classval, probsval)]
  class_and_probs = np.reshape(class_and_probs, dims)
  for i in range(0, len(images)):
    print('Image: ' + images[i])
    for j in range(0, 5):
      print(class_and_probs[i][j])


def predict_and_profile(host, port, model, batch):

  # Prepare the RPC request to send to the TF server.
  channel = implementations.insecure_channel(host, int(port))
  stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
  request = predict_pb2.PredictRequest()
  request.model_spec.name = model

  # 'predict' is the default signature used for canned estimators and the
  # preferred signature. If you used a different signature when creating the
  # servable model, be sure to change the line below.
  request.model_spec.signature_name = 'predict'  # TODO: change if necessary

  request.inputs['images'].CopyFrom(
      tf.contrib.util.make_tensor_proto(
          batch,
          shape=[len(batch)],
          dtype=tf.string
      )
  )

  # Call the server to predict, return the result, and compute round trip time
  start_time = int(round(time.time() * 1000))
  result = stub.Predict(request, 60.0)  # 60 second timeout
  elapsed = int(round(time.time() * 1000)) - start_time

  return result, elapsed

if __name__ == '__main__':
  main()
