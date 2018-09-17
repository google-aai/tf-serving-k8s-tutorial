# Building a Servable TensorFlow Model

The primary difference between a servable model and a training model is how the
model is called during prediction. Typically in training, a data scientist will
bundle multiple images and labels into records, and generate samples using APIs
such as [TensorFlow datasets](https://www.tensorflow.org/guide/datasets). In
some cases, the images ingested from datasets are also run through TensorFlow
graph components that randomly perturb the image to improve robustness in the
model, e.g. rotating, mirroring, or making slight changes to pixel values.
However, when serving a model for prediction, users typically want to predict
the class for the image as is.

We provide two options for this exercise:
[Estimators](https://www.tensorflow.org/guide/estimators) and
[Keras](https://keras.io/), both which are popular abstractions of choice used
by many data scientists and researchers to train models. Keras is a high level
API that makes it very easy to implement and train a model.
However, it lacks the flexibility of control and functionality that Tensorflow
has (e.g. optimizer types, custom visualization/logging, less conventional
model/graph components, etc.), which Estimators can support as part of its API. 

We recommend working through the Keras exercise if you are less experienced with
TensorFlow. We encourage more experienced TensorFlow users to run through the
Estimators Exercise, as it contains more refactoring, debugging, and unit
testing examples.

**Exercises:**

In the Jupyter directory window under `work`, cd into `tf-serving-k8s-tutorial`,
open the notebook
[estimator_training_to_serving.ipynb](./estimator_training_to_serving.ipynb),
and work through the exercises in there to convert a model trained by the
[Tensorflow Estimator API](https://www.tensorflow.org/programmers_guide/estimators)
into a servable "saved model" format. You can also try out
[keras_training_to_serving.ipynb](./keras_training_to_serving.ipynb)
to do the same exercise with a prepackaged [Keras](https://keras.io/) model
trained/loaded with a Tensorflow backend. 

Note that we've chosen these two API as they are perhaps the most popular
abstractions of choice used by many ML researchers and practitioners. However,
one can also build a servable directly from a TF graph using
tf.saved_model.builder.SavedModelBuilder(). The exported model format will
be identical regardless of the API used, as long as there is specification for
how the model should receive input and return output.

If you are stuck, please refer to the solution notebooks for hints:
[estimator_training_to_serving_solution.ipynb](./estimator_training_to_serving_solution.ipynb)
and [keras_training_to_serving_solution.ipynb](./keras_training_to_serving_solution.ipynb).

### Unit Test your Code

The Estimator and Keras notebooks demonstrate how one can refactor training
code into production code in order to perform unit testing. Additionally,
we have provided samples from the
[Tensorflow unit testing](https://www.tensorflow.org/api_guides/python/test) and
[Tensorflow Eager](https://research.googleblog.com/2017/10/eager-execution-imperative-define-by.html)
frameworks for the interested reader. These are both helpful tools to help you
debug Tensorflow functions that would otherwise be part of an end-to-end
Tensorflow graph. Note that unit testing is a more formal software engineering
framework, while Eager is more data science-driven (You can immediately validate
the result of running data through a Tensorflow graph as you construct it.)

### Validate your Servable Model

After successfully exporting your servable model to disk, it helps to verify
that the model can read the expected request format before proceeding to
Dockerize and deploying to a Kubernetes cluster. The notebook
[resnet_servable_validation.ipynb](resnet_servable_validation.ipynb) contains
code to validate that your servable Resnet model performs the right operations
in terms of input and output.

**Note:** if you plan to run on GPU and use data_format=“channels_first” in
the Estimator model for GPU deployment, please remember to start with
“channels_last” for this validation step, and then create a new model with
“channels_first” to test on your GPU cluster later on.

**If you made it here, congratulations!** 
[Continue on here](README.md#serving-your-model) to learn how to serve your
model!