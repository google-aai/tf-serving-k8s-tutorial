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

"""Sample tensorflow eager execution for helper functions.

Make sure to create a new virtual environment (Python 3, TF 1.5)
before executing this!
"""

import tensorflow as tf
import tensorflow.contrib.eager as tfe
from helper_functions import preprocess_image

tfe.enable_eager_execution()

# Test preprocess_image
with open("../client/cat_sample.jpg", "rb") as imageFile:
  jpeg_str = imageFile.read()
  result = preprocess_image(jpeg_str)
  assert result.shape == (224, 224, 3)
  assert tf.reduce_max(result) <= 0.5  # Notice tf functions here!
  assert tf.reduce_min(result) >= -0.5

