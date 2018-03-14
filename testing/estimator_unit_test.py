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

"""Sample tensorflow unit testing for helper functions.

Also includes an exercise for integration testing.

Run this in your Jupyter notebook (python 3.6) virtual environment.
"""

import numpy as np
import tensorflow as tf
from helper_functions import serving_input_to_output
from helper_functions import preprocess_image, preprocess_input
from helper_functions import postprocess_output


class PreprocessImageTest(tf.test.TestCase):
  '''Test the helper function preprocess_image using a sample jpeg.'''
  def testJpegDecoding(self):
    with open("../client/cat_sample.jpg", "rb") as imageFile:
      jpeg_str = imageFile.read()
      with self.test_session():
        x = preprocess_image(jpeg_str)
        result = x.eval()
        # Good practice is to hard code test cases to catch errors in constants.
        self.assertAllEqual(result.shape, (224, 224, 3))
        self.assertLessEqual(result.max(), 0.5)
        self.assertGreaterEqual(result.min(), -0.5)


def split_digits(input):
  return input


class InputTest(tf.test.TestCase):
  '''Test the helper function preprocess_image using a sample jpeg.'''

  def testPreprocessInput(self):
    with open("../client/cat_sample.jpg", "rb") as imageFile:
      jpeg_str = imageFile.read()

      # NOTE: Always wrap your arrays with numpy!
      # If you do not, you may end up with strange bugs since TF expects
      # numpy arrays.
      input = {'images': np.array([jpeg_str, jpeg_str])}

      with self.test_session():
        # Duplicate jpeg for length 2 tensor
        x = preprocess_input(input)
        result = x.eval()
        self.assertAllEqual(result.shape, (2, 224, 224, 3))
        self.assertLessEqual(result.max(), 0.5)
        self.assertGreaterEqual(result.min(), -0.5)
        self.assertAllEqual(result[0], result[1])


class OutputTest(tf.test.TestCase):
  '''Test the helper function postprocess_output.

  Note that you can add multiple test cases in the same class.
  '''

  def testPostprocessOutputSame(self):

    # NOTE: Always wrap your arrays with numpy!
    # If you do not, you may end up with strange bugs since TF expects
    # numpy arrays.
    logits = np.ones(1001)

    with self.test_session():
      # Duplicate jpeg for length 2 tensor
      x = postprocess_output(logits)
      classes = x['classes'].eval()
      probs = x['probabilities'].eval()
      # Inefficient but simple element-wise check
      self.assertAllEqual(probs[1:], probs[:-1])
      self.assertAllClose(probs, len(probs) * [1.0/1001.0], 1e-6)

  def testPostprocessOutputDifferent(self):

    # NOTE: Always wrap your arrays with numpy!
    # If you do not, you may end up with strange bugs since TF expects
    # numpy arrays.
    logits = np.ones(1001)
    logits[2] = 2.5
    logits[5] = 3.5
    logits[10] = 4
    logits[49] = 3

    with self.test_session():
      # Duplicate jpeg for length 2 tensor
      x = postprocess_output(logits, 4)
      classes = x['classes'].eval()
      probs = x['probabilities'].eval()
      # Inefficient but simple element-wise check
      self.assertEqual(len(probs), 4)
      self.assertEqual(len(classes), 4)
      self.assertEqual(classes[0], 10)
      self.assertEqual(classes[1], 5)
      self.assertEqual(classes[2], 49)
      self.assertEqual(classes[3], 2)


class IntegrationTest(tf.test.TestCase):
  '''Test that preprocessing-network-postprocessing works correctly.

  Note that this test does not test the results of an actual trained network,
  but merely verifies that tensorflow input and output formats are hooked up
  consistently. Test cases here are not as important as ensuring that the graph
  actually builds without raising errors.

  Data validation of output results is handled in the
  `resnet_servable_validation` notebook.
  '''

  def testInputToOutput(self):
    input = {'images': tf.placeholder(
      dtype=tf.string, shape=[None], name='test_jpeg_tensor')}
    output = serving_input_to_output(input, tf.estimator.ModeKeys.PREDICT)
    self.assertEqual(len(output), 2)
    self.assertEqual(output['classes'].dtype.as_numpy_dtype, np.int32)
    self.assertEqual(output['probabilities'].dtype.as_numpy_dtype, np.float32)
    self.assertAllEqual(output['classes'].get_shape().as_list(), [None, 5])
    self.assertAllEqual(output['probabilities'].get_shape().as_list(), [None, 5])


if __name__ == '__main__':
  tf.test.main()