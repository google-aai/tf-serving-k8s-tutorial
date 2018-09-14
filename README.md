# Deploying Tensorflow Serving using Kubernetes Tutorial

TODO: README is currently DEPRECATED. It will be updated after Strata Data
 Conference in NY. Please switch to tag `march-2018` for a working tutorial
 from Strata Data Conference San Jose.

### What this project covers
This project is a tutorial that walks through the steps required to deploy and
[serve a TensorFlow model](https://www.tensorflow.org/serving/serving_basic)
using [Kubernetes (K8s)](https://kubernetes.io/).

The key concepts covered in this tutorial are as follows:

* Convert a TensorFlow(TF) graph trained through various APIs into a servable
model
* Serve the model using Tensorflow Serving, deployed via [KubeFlow](kubeflow.org)
* Send online prediction requests to the cluster via a client. Profile latency
and throughput. Experiment with different batch sizes.
* Visualize image pixel contributions to model predictions to explain how the
model sees the world.

## Setup

Before the fun begins, we need to setup our environment and K8s clusters. 

As a developer, it often helps to create a local deployment prior to deploying
on the cloud. Local deployment is challenging in that one's local environment
varies significantly between individuals. It is up to the student to figure out
how to setup and validate the following required software for emulating a K8s
cluster locally. We offer some guides on setting up a local K8s cluster, as well
as setting up a cluster on Google Cloud Platform (GCP):

* [Local: Minikube](LOCAL_SETUP.md)
* [Cloud: Google K8s Engine](GKE_SETUP.md)

### Additional Required Software

* [Python 2.7+](https://www.python.org/): The TensorFlow Serving API currently
runs in Python 2, so you will need to make client requests to your model server
using Python 2.
* [Docker](https://www.docker.com/): to build images that can be deployed on K8s
* [Git](https://git-scm.com/): so you can access this project and other projects
* [Pip](https://pip.pypa.io/en/stable/installing/): to install Python packages
required for the tutorial
* [Ksonnet](https://github.com/ksonnet/ksonnet): follow the install instructions
in github

## Deploy KubeFlow onto your cluster

[KubeFlow](kubeflow.org) is always in an active stage of development, so we will
be using a stable tag v0.2.5. Run the following command to deploy KubeFlow onto
your Kubernetes cluster:

```
cd ~
curl https://raw.githubusercontent.com/kubeflow/kubeflow/v0.2.5/scripts/deploy.sh | bash
```

Next, run the following command to check on your pods and services. The services
should be up almost immediately, but pods may take longer to create.

```
kubectl get svc
```

```
kubectl get pods
```

**Troubleshooting:** For troubleshooting, see here.



## Accessing JupyterHub and Spinning up a Notebook

![notebook everywhere](img/notebook_everywhere.png)

JupyterHub is a popular K8s notebook spawner that can spin up Jupyter
servers on demand for an entire team of data scientists, each server having its
isolated set of customized resources (disk, memory, accelerators).
When a data scientist is finally done training and fine-tuning a model for
production, it is important to be able to export this model for serving. The
following exercises will be running through how to export a model from a local
Jupyter server into a location that K8s can access and serve using the
TensorFlow Serving app.

To access your Jupyter notebook environment, you will need to use port forwarding
from your local computer. 

```
JUPYTER_POD=`kubectl get pods --selector="app=tf-hub" --output=template --template="{{with index .items 0}}{{.metadata.name}}{{end}}"`
kubectl port-forward ${JUPYTER_POD} 8000:8000
```

Go to your browser and access JupyterHub here:

```
localhost:8000
```

You should see a login screen like this:
![jupyter login](img/jupyterhub_login.png)

Type in any username and password to spin up a local environment (Note: if the
username does not exist, a new Jupyter server will be created for that user
with its own isolated resources. If the username already exists, the password
will be required to match the one used to create the server, and you will end up
in the previously created server environment.)

The next page, if you are creating a new environment, should have a drop down
menu with images, and separate CPU, memory, and extra resource text boxes.
In the dropdown menu, select the TensorFlow 1.8 CPU image:

![jupyterhub tf 1.8 cpu](img/jupyterhub_kubeflow_img.png)

Set CPU and memory to whatever your cluster can handle. 1 CPU and 2Gi memory is
sufficient for the exercises, but if you are on a cluster and can afford more
resources, more CPU and memory will allow you to spin up and run notebooks
faster without having to shut down notebook kernels.

The notebook server may take a few minutes to spin up depending on cluster
resources, so be patient. Once it has spun up, go into the work directory,
and upload the local notebook `./jupyter/download_models_and_notebooks.ipynb`
into this directory. In your notebook, run all the cells to download the
Resnet50 models, project notebooks, and library dependencies required for the
next part of this exercise.

## Create a Servable Resnet Model from Estimator and Keras APIs

Now that all of the environment setup is out of the way, let’s create a servable
model! 

[Run the exercises here](SERVABLE_MODEL.md) (solutions included).


## Running TensorFlow Serving on Your Packaged Model

### The Challenge

Your data scientists in JupyterHub have decided that a set of models generated
in a few Jupyter servers are ready for serving in production. JupyterHub
by default creates a
[persistent volume (pv)](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
and attaches a
[persistent volume claim (pvc)](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims)
to that volume which only allows the user who spawned the notebook to access
that volume. (To be more precise, the pv and pvc are attached to the 
[pod](https://kubernetes.io/docs/concepts/workloads/pods/pod/) that is used to
hold the user's requested cluster resources and isolate the user's work
environment). Unfortunately, no other users/pods are allowed to access this
environment without setting permissions without reconfiguring the volume to
accept multiple pods to read and write.

Fortunately, we have two options to handle this: by changing
options for k8s pv, or by serving the model from cloud storage!

### Setting up TF Serving for your Model

To deploy TensorFlow Serving with KubeFlow, we will need a number of steps.
First cd into your `kubeflow-ks-app` directory, and generate a tf-serving
template fron the KubeFlow repository.

```
ks generate tf-serving my-tf-serving
```

`tf-serving` is the KubeFlow template name, and `my-tf-serving` is the
app name (which you can name whatever you want).

Next, we will need to configure the app using [ksonnet](ksonnet.io). Follow the
two options below depending on where you running this exercise:

[Follow the instructions here](SERVING_ON_PREM.md) for a general TensorFlow
Serving deployment using KubeFlow for local (minikube) and on-prem clusters.

[Follow the instructions here](SERVING_ON_GKE.md) for serving on the Google
Cloud Platform using GKE. While we do not explicitly provide an example here,
similar configuration paths exist for Amazon EKS and Microsoft AKS.

### Setup port forwarding

Once you have your serving pod running, use port forwarding on port 9000 to
enable secure access to your model server:

```
kubectl port-forward ${SERVING_POD} 9000:9000
```


## TF Client

### Setup

If you choose to use Google cloud to host a client, a [setup script](gcp/setup_client_vm.sh)
already exists for deploying all required libraries on a compute engine VM.

The following steps below are for setting up a client locally.

First, create a *Python 2* virtual environment.

```
deactivate  # Run only if you need to exit the Python 3 virtual environment.
virtualenv <path/to/client-virtualenv>
source <path/to/client-virtualenv>/bin/activate
```

cd into the tutorial project directory (`tf-serving-k8s-tutorial`), and run:

```
pip install -r client_requirements.txt
```

Then cd into the client directory within the tutorial project:

```
cd client
```

To run the client, enter the command:

```
python resnet_client.py --server <load-balancer-external-ip> \
  --port 9000 \
  <image-path-or-url-1> <image-path-or-url-2> ...
```

For the external-ip, if you are using minikube, the ip should be `localhost`.
If you are running on Google Cloud, you can find the ip by running
`kubectl get svc`.

For the image paths and/or urls, you can use the cat_sample.jpg in the current
directory, or you find some RGB pictures online, such as:
https://www.popsci.com/sites/popsci.com/files/styles/1000_1x_/public/images/2017/09/depositphotos_33210141_original.jpg?itok=MLFznqbL&fc=50,50

![you just got served](img/you_got_served.png)

### Profiling Latency

**Exercise:**: Look at the profiler [resnet_profiler.py](client/resnet_profiler.py).
Try sending requests with the profiler and compute latency and throughput.
Latency is simply the round trip delay returned by the profiler. An
approximation of throughput is the number of batches divided by latency when a
large batch size is used. Try varying batch sizes between 1 and 256.

What do you notice about CPU/GPU performance with different batch sizes?

**Remark:** Profiling is a very important step when you are trying to setup a
robust server. GPUs are great performers, but stop providing gains after a
certain batch size. Furthermore, servers can run out of memory, in which case TF
serving often crashes silently, i.e. `kubectl logs <pod>` won't return anything
useful. When you deploy your own Kubernetes system, you will need to ensure that
your machine can load your model and process requested batch sizes.

## Model Understanding and Visualization

As a bonus feature, we offer ways to validate a served model through
visualization! Run this notebook:

```
resnet_model_understanding.ipynb
```

The notebook runs a visualization of pixels that are important in determining
that the image belongs to a particular class. More specifically, the visible
pixels correspond to the highest partial derivatives of the logit of the most
probable class as a function of each pixel, integrated over a path of image
pixels from a blank image (e.g. all grey pixels) to the actual image.
The visualization is based on a recent research paper by M. Sundararajan,
 A. Taly, and Q. Yan: [Axiomatic Attribution for Deep Networks](https://arxiv.org/pdf/1703.01365.pdf).

## Additional Resources

### General Disclaimers and Pitfalls

* Tensorflow Server is written in c++, so any Tensorflow code in your
model that has python libraries embedded in it (e.g. using tf.py_func()) will
FAIL! 
* Security is an issue in this tutorial! Simply changing your model server to a
`LoadBalancer` to open up a tcp port for serving is not secure! If you are
running on cloud, you will need to enable secure identity for your K8s cluster,
such as Google Cloud IAP.
[See the Kubeflow IAP documentation](https://github.com/kubeflow/kubeflow/blob/master/docs/gke/iap.md)
for more information. 

### KSonnet and Kubeflow

* [Kubeflow](https://github.com/kubeflow/kubeflow) automates Kubernetes
deployments for TF notebook, model training (distributed and GPU), and model
serving. Much of this tutorial's content (i.e. deploying TF serving) can be
automated using their solutions. Please check out their project and contribute
to the discussion!
* [ksonnet.io](https://ksonnet.io/tour/welcome) Ksonnet allows you to define
functions that take in parameters that determine
the value of fields set in your yaml file. Furthermore, these parameter values
can be configured at the command line for different environments. Try out their
tutorial!


