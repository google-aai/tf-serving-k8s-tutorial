# Deploying Tensorflow Serving on Kubernetes

The following tutorial shows how to deploy Tensorflow Serving locally (using
VirtualBox and Minikube) as well as on Google Kubernetes Engine (GKE). The key
objectives of this tutorial are as follows:

* Introduce the tools needed to deploy tf-serving on k8s clusters
* Convert a graph trained using the Tensorflow estimator API into a servable
model format.
* Build the servable model into a docker image
* Push the docker image to a docker container registry
* Deploy the docker image from the registry onto a Kubernetes cluster, where
each container created will be serving the model. Also deploy a external
load balancer to receive incoming requests and send to different backend
containers.
* Send images to the cluster using a client, and receive classification results.
* Bonus: Run a notebook to analyze the importance of pixels of an image on its
final classification result.



## Setup

### Installation

To create and manage your Kubernetes(K8s) cluster from your local machine,
download and install the following:

* [docker](https://www.docker.com/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): if you
have [Google Cloud SDK](https://cloud.google.com/sdk/) installed, you can also 
install kubectl using the command `gcloud components install kubectl`

### Environment Settings

Follow these links to setup your K8s environment:
* [Local: Minikube](LOCAL_SETUP.md)
* [Cloud: Google K8s Engine](GKE_SETUP.md)

## Create a Servable Resnet Model

We are going to be creating a servable Resnet model that was trained on
Imagenet. You will be working with the notebook:

```
resnet_training_to_serving.ipynb
```

There are three options for running this step: locally or via Jupyterhub. We
recommend using Jupyterhub for educational purposes, as it will teach you
how to run Jupyter from within Docker and K8s.

### 1. Create Servable Model in default environment

If you would like to run the
notebook in your local environment, create a python 3.5+ virtual environment
and activate it first, e.g.

```
virtualenv -p python3 <path/to/environment>
source <path/to/environment>/bin/activate
```

Within the virtual environment, install dependencies and run the notebook:

```
pip install -r jupyter_requirements.txt
jupyter notebook
```

### 2. Use Google Cloud Datalab

(For Google Cloud users only!)

If you want to avoid the hassle of creating your own environment to run
a jupyter notebook, you can use Google Cloud Datalab. Open your 
[Google Cloud console](https://console.cloud.google.com) and in the top right
corner, click the ">_" icon to open a cloud shell in your browser. Then execute
the command:

```
datalab create <datalab-instance-name>
```

If you'd like to create an instance with gpu, cloud supports it in beta version:
```
datalab beta create-gpu <datalab-instance-name>
```

Wait a few minutes for the datalab process to complete and ssh keys to
propagate. Afterwards, you can upload the notebooks in this project to datalab.

If you have [created a storage bucket]() for this lab, you can run an
additional command at the end of your `resnet_training_to_serving.ipynb`
notebook to write the resnet_servable directory to your bucket:

```
!gsutil -m cp -r ./resnet_servable gs://<your-bucket>/resnet_servable
```

This model becomes accessible from any GKE machine.

### Create Servable Model on Jupyterhub

If you would like to run your notebook on your K8s cluster itself, Kubeflow
contains a Jupyterhub component that allows you to do just that. Follow the
[quick start instructions](https://github.com/kubeflow/kubeflow/blob/master/README.md#quick-start)
and continue through the [user guide](https://github.com/kubeflow/kubeflow/blob/master/user_guide.md)
to spin up your notebook.

When you are done creating your model, use the directory tree to find your model
files (resnet_servable/...), and download them to this project's base directory with
the same nested directory structure, i.e. resnet_servable/<number>/...

## Create a Model Server Docker Image

### Docker files and docker images
Docker images are snapshots of a virtual environment (operating system,
installed software, files, etc.) and are often built on top of other Docker
images. For example, the docker file `Dockerfile.cpu` has the following line:

```
FROM gcr.io/kubeflow/model-server:1.0
```

This line references an image `gcr.io/kubeflow/model-server:1.0` as a
starting point (base image) for building a new image. Additional commands can be
added in the docker file to modify the base image. This can include installing
new software, uploading files from your local environment, etc. When 
`docker build` is run, a new image will be created with these commands executed
on the base image.

Docker images are composed of many layers of images upon which
previous images are built. To make a new image accessible for deployment or for
further image builds, a locally built image will need to be pushed into a
*registry*, such as [Docker Hub](https://hub.docker.com/) or
[Google Container Registry](https://cloud.google.com/container-registry/).

### Docker file exercise

We would like to add docker images into the
The Dockerfile.cpu and Dockerfile.gpu files will add a resnet_serving directory
to the image, and copy your model into the image. It will also copy a batching
configuration file `batching.conf`.  file which serves as an extra argument into
the Tensorflow Model Server. To run a docker file, make sure you are in this
project's main directory. Set your shell variable first to either cpu or gpu,
and then proceed:

```
MACHINE_TYPE=cpu|gpu
```

Run through the exercise by editing the docker build that you wish to build.
The dockerfile to edit is `Dockerfile.$MACHINE_TYPE`.

After editing the file, build the docker image. 

```
docker build -t library/resnet-server-$MACHINE_TYPE:1.0 \
 -f Dockerfile.$MACHINE_TYPE .
```

If the build succeeds, run the image in interactive mode to check that your
model directory was correctly copied, e.g.

```
IMAGE=library/resnet-server-$MACHINE_TYPE:1.0
docker run -it ${IMAGE}
```

then inside your docker, check that your model directory is there:

```
cd resnet_servable
ls
```

Type `exit` to exit your docker image.

Now you will need `docker push` to push your image to a
location where they can be deployed on a kubernetes cluster. 

## Pushing the Docker Image to a Container Engine

### Local Minikube Container Engine

If you already followed the setup instructions for
docker and minikube, you should have a docker container engine running on
minikube that has ssh port forwarding to localhost.
You can push to localhost:5000:

```
docker tag library/resnet-server localhost:5000/${IMAGE}
docker push localhost:5000/${IMAGE}
```

### Google Container Engine

Make sure you setup som
Tag your docker image and push it to the Google Cloud container registry using
the `gcloud docker` command:

```
docker tag ${IMAGE} gcr.io/${PROJECT}/${IMAGE}
gcloud docker -- push gcr.io/${PROJECT}/${IMAGE}
```

## Edit Kubernetes Configuration Files

If you have multiple clusters running (e.g. minikube and GKE), check that your
kubectl is pointing to your intended cluster by default, and switch if
necessary. [See here](KUBECTL_BASICS.md).

We will now modify a yaml file to deploy the container and a front end load
balancer to your kubernetes cluster. Copy the file
`k8s_resnet_serving_template.yaml` over and fix the TODO lines:

```
cp k8s_resnet_serving_template.yaml k8s_resnet_serving.yaml
# Edit k8s_resnet_serving.yaml
```

Note that the yaml file will create a LoadBalancer service, and a backend
deployment. The backend deployment consists of pods (replicas) that require
different types and amounts of resources on your cluster. If your cluster has
insufficient resources, you will only spin up a number of pods based on what
is available.

Run the following to deploy your pods and the load balancer service:
```
kubectl create -f k8s_resnet_serving.yaml
```

Run get and edit commands to check on the progress of your pod deployment. The
Tensorflow Server should be ready once you see the log display 

The LoadBalancer service exposes a public port (9000). Running the following
will show you all of the active services on your cluster. You will see your
load balancer service (resnet-service) with an external IP address:

```
kubectl get svc
```

## TF Client

From the strata2018 project directory, create a *Python 2* virtual environment,
and run:

```
pip install -r client_requirements.txt
```

Next run the resnet client. You can list as many images as you'd like:
```
python resnet_client.py --server <load-balancer-ip> --port 9000 <image1> <image2> ...
``` 

If you are using GKE, you can also spin up a vm on
[Compute Engine](https://cloud.google.com/compute/) and checkout this project
there to run your client. This can speed up the network transmission times
such that you have a better way to profile the speed of your predictions.

### Profiling Latency and Throughput with the Client

A couple options in the client can be used to profile the serving latency
and throughput of the client. 

* The flag --profile_only silences the output
classes and probabilities and simply returns the round trip prediction time
in milliseconds. 
* The flag -r creates 2^r copies of the images specified and sends the batch
to the server.

**Note:** Tensorflow Serving on GPU can sometimes fail silently if the GPU
runs out of memory! You will need to carefully tune your batch size to optimize
performance while preventing OOM errors. For example, if -r is set too large,
the pod can crash due to out-of-memory errors, and you will need to wait about
a minute for a new pod to boot in the background before calling the service
again. You will receive an rpc error from the client if the pod breaks. You
can also view the status of your pod using `kubectl get pods`.

## Scaling up your application

If you wish to scale up your deployment without shutting down the currently
deployed pods, you can run:

```
kubectl scale --replicas=<num-pods> resnet-deployment
```

When you direct a client request to the load balancer, it will use
an elastic search algorithm to assign your request to one of the backend pods.

## Auto-refreshing the model version on GKE

Suppose your ML researcher has a new and improved Resnet model, or even a new
architecture (e.g. 152-layers!). Tensorflow serving has the feature of
immediately picking up the newest version of a servable model in your servable
directory, and serving it immediately! All you need to do is make sure that
the numeric identifier (the directory inside your serving model directory,
default is unix timestamp) is greater than the previous version. You can use
an updated notebook to export a new servable model.
  
Unfortunately, building a new docker image requires you to redeploy your
containers/pods, which interrupts your service. However, Google Kubernetes
Engine has access to Google Storage as well, so you can reference a storage
bucket as your model path and simply add/update the directory on the bucket
itself! To test this out, select a bucket name:

```
BUCKET=<your-bucket-name>
```

and then create it:

```
gsutil mb gs://${BUCKET}
```

Upload your servable model  directory to the bucket:

```
gsutil -m cp -r /local/path/to/servable_dir gs://${BUCKET}/<servable-dir>
```

Now edit your yaml file to point to your Google Storage directory. Any time
you upload a new model version into that directory, TF model server should
pick it up.

## Bonus feature: Model Understanding

Using either your local environment or a Kubernetes Cluster deployment of
Jupyterhub, run the notebook:
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

### KSonnet and Kubeflow

Much of this tutorial borrows configurations and docker images out of
[Kubeflow](https://github.com/kubeflow/kubeflow), or are otherwise customized
from their project. After completing this tutorial, please check out their
project for convenient libraries for deploying end-to-end deployment solutions
for Tensorflow serving using [ksonnet](https://github.com/ksonnet).

Ksonnet allows you to define functions that take in parameters that determine
the value of fields set in your yaml file. Furthermore, these parameter values
can be configured at the command line for different environments. 

For example, if you want 1 replicas (pod) deployed on minikube but 5 on GKE,
you can create a ksonnet function that takes in `replicas` as a parameter.
You then specify two environments (e.g. minikube and cloud) and set parameters
for each environment, e.g. `ks param set $COMPONENT_NAME replicas 5 env=cloud`.
To learn more about ksonnet:

* [ksonnet.io](https://ksonnet.io/tour/welcome) offers a tutorial showing how to
deploy and scale an app. 
* [Kubeflow](https://github.com/kubeflow/kubeflow) is a great resource for
examples using ksonnet to deploy TF notebook, jobs, and serving. It also
includes various prototypes used to generate the ksonnet files.

## Disclaimers and Pitfalls

* Tensorflow Server is written in c++, so any Tensorflow code in your
model that has python libraries embedded in it (e.g. using tf.py_func()) will
FAIL! 
* Security is an issue in the demo above! Simply changing your model server to a `LoadBalancer` to open up
a tcp port for serving is not secure! Google Cloud IAP enables secure
identity. [See the Kubeflow documentation](https://github.com/kubeflow/kubeflow/blob/master/docs/gke/iap.md)
for more information. 
