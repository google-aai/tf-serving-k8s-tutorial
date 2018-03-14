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

"""Helper functions from Estimator API unit testing.

These helper functions are assumed to be part of PRODUCTION code, which are
created by modifying and refactoring the ResNet50 Estimator training code into
reusable and testable modules.

Remember to checkout the Tensorflow models directory from the parent directory
of this tutorial to ensure that this code will work correctly!

Run this in your Jupyter notebook (python 3.6) virtual environment.
"""

import tensorflow as tf

# The following is a hacky way to load resnet_model into the python path
# assuming you followed the README to download the models repository.
# DO NOT do this in practice! Ensure that the TF model code you intend to
# serve lives in the same python project!
import sys, os
sys.path.append(os.path.join(
  os.path.dirname(__file__), '../../models/official/resnet'))
from resnet_model import imagenet_resnet_v2

# Constants
_DEFAULT_IMAGE_SIZE = 224
_LABEL_CLASSES = 1001
RESNET_SIZE = 50
TOP_K = 5

def preprocess_image(encoded_image):
  '''Preprocesses the image by subtracting out the mean from all channels.
  Args:
    image: A jpeg-formatted byte stream represented as a string.
  Returns:
    A 3d tensor of image pixels normalized to be between -0.5 and 0.5, resized
      to height x width x 3. The normalization is an approximation of the
      preprocess_for_train and preprocess_for_eval functions in
      https://github.com/tensorflow/models/blob/v1.4.0/official/resnet/vgg_preprocessing.py.
  '''
  image = tf.image.decode_jpeg(encoded_image, channels=3)
  image = tf.to_float(image) / 255.0 - 0.5
  return image


def preprocess_input(features):
  '''Function to preprocess client request before feeding into the network.

  Use tf.map_fn and the preprocess_image() helper function to convert the
  1D input tensor of jpeg strings into a list of single-precision floating
  point 3D tensors, which are normalized pixel values for the images.

  Then stack and reshape this list of tensors into a 4D tensor with
  appropriate dimensions.

  Args:
    features: request received from our client,
      a dictionary with a single element containing a tensor of multiple jpeg
      images, i.e. {'images' : 1D_tensor_of_jpeg_byte_strings}

  Returns:
    a 4D tensor of normalized pixel values for the input images.

  '''
  images = features['images']  # A tensor of tf.strings
  processed_images = tf.map_fn(preprocess_image, images, dtype=tf.float32)
  processed_images = tf.stack(
    processed_images)  # Convert list of 3D tensors to a 4D tensor
  processed_images = tf.reshape(
    tensor=processed_images,
    shape=[-1, _DEFAULT_IMAGE_SIZE, _DEFAULT_IMAGE_SIZE, 3]
  )
  return processed_images


def postprocess_output(logits, k=TOP_K):
  '''Return top k classes and probabilities from class logits.'''
  probs = tf.nn.softmax(logits)
  top_k_probs, top_k_classes = tf.nn.top_k(probs, k=k)
  return {'classes': top_k_classes, 'probabilities': top_k_probs}


def serving_input_to_output(features, mode, k=TOP_K):
  '''End-to-end function from serving input to output.'''

  # Preprocess inputs before sending tensors to the network.
  processed_images = preprocess_input(features)

  # Build network graph and connect to processed_images
  network = imagenet_resnet_v2(RESNET_SIZE, _LABEL_CLASSES,
                               data_format='channels_last')
  logits = network(inputs=processed_images,
                   is_training=(mode == tf.estimator.ModeKeys.TRAIN))

  # Postprocess network output (logits) and return top k predictions.
  predictions = postprocess_output(logits, k=k)
  return predictions