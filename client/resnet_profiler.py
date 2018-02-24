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

"""A profiler client that prints statistics on the round trip serving time.

The profiler makes the same request as resnet_client.py, but computes the round
trip serving time for the request. You can set the number of times you would
like to send requests, and the profiler will compute various statistics on the
serving times, such as mean, median, min and max.
"""

from __future__ import print_function

import argparse

import numpy as np

from image_processing import preprocess_and_encode_images
from resnet_client import predict_and_profile


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
      '-r',
      '--replications',
      type=int,
      default=1,
      help='How many times to replicate samples to send a larger batch size'
  )
  parser.add_argument(
      'images',
      type=str,
      nargs='+',
      help='Paths (local, GCS, or url) to images you would like to label'
  )
  parser.add_argument(
      '-n',
      '--num_trials',
      type=int,
      default='.txt',
      help='File used to log batch serving request delays. Will create file'
           'if it does not exist. Otherwise, it will append to the file.'
  )
  args = parser.parse_args()

  # Preprocess images at the client and compress as jpeg
  img_size = args.dim
  images = args.images

  jpeg_batch = preprocess_and_encode_images(images, img_size)

  # Create r copies of the array for profiling.
  batch_array = []
  for i in range(0, args.replications):
    batch_array = np.append(batch_array, jpeg_batch, axis=0)
  batch_size = len(batch_array)
  print("Batch size: " + str(batch_size))

  # Call the server num_trials times
  elapsed_times = []
  for t in range(0, args.num_trials):
    # Call the server to predict top 5 classes and probabilities, and time taken
    result, elapsed = predict_and_profile(
        args.server, args.port, args.model, batch_array)
    # Print and log the delay
    print('Request delay: ' + str(elapsed) + ' ms')
    elapsed_times.append(elapsed)

  print('Mean: %0.2f' % np.mean(elapsed_times))
  print('Median: %0.2f' % np.median(elapsed_times))
  print('Min: %0.2f' % np.min(elapsed_times))
  print('Max: %0.2f' % np.max(elapsed_times))


if __name__ == '__main__':
  main()
