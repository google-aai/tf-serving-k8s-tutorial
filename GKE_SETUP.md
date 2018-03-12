# Google Kubernetes Engine Setup

## Prerequisites

Make sure you have the [Chrome browser](https://www.google.com/chrome/)
installed. (Firefox may work, but we make no guarantees!)

Next, make sure you sign up for a
[Google Cloud account](https://cloud.google.com/), and 
[create a project](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
with a billing account attached.

Optional: If you wish to experiment with GPU accelerators on your k8s cluster,
you will need to first
[enable Compute Engine API](https://console.cloud.google.com/compute/instances),
and then select a [GPU enabled zone](https://cloud.google.com/compute/docs/gpus/)
and [request additional quota](https://console.cloud.google.com/iam-admin/quotas)
for your project based on how many nodes and GPUs you wish to have. This may
take a couple days for the cloud team to review, and may require a monetary
deposit! This is an important step if you are planning to use elements from the
tutorial to implement a production serving system with low latency and high
throughput. However, the tutorial exercises themselves do not require GPUs. CPU
and GPU k8s deployment exercises are nearly identical.

## Creating a K8s Cluster

From the [cloud console](console.cloud.google.com) page, click the
![cloud shell](./img/gcp_shell.png) icon at the top right to open up cloud
shell. Inside the shell, assuming you have at least one project in your account,
check that your project is set to the one you wish to use:

```
gcloud config list project
```

If you need to switch projects, or your project is not already set, run:

```
gcloud config set project <project-name>
```

[Choose a zone](https://cloud.google.com/compute/docs/gpus/) to spin up your
Kubernetes cluster. For GPU users, you will need to use the
[GPU enabled zone](https://cloud.google.com/compute/docs/gpus/) that you chose
above when requesting quota:

```
gcloud config set compute/zone <zone>
```

Use git to checkout the tutorial for future use:

```
git clone https://github.com/google-aai/tf-serving-k8s-tutorial.git
```

Spin up a Kubernetes cluster in your preferred zone. You can change num-nodes to
any number of machines depending on how you'd like to scale your deployment, but
keep in mind that larger clusters require more cpu/gpu resources as the settings
are usually per node. Below we've defaulted to a 2 node cluster.

**CPU Cluster**: Run the following command:

```
gcloud container clusters create kubernetes-cluster \
  --scopes storage-rw \
  --machine-type n1-highmem-4 \
  --num-nodes 2 \
  --image-type UBUNTU
```

**GPU Cluster**: GCP supports two accelerator types in production:
`nvidia-tesla-k80` and `nvidia-tesla-p100`. Run the following to spin up a
cluster of 2 nodes with 1 GPU each:

```
ACCEL_TYPE=nvidia-tesla-k80 | nvidia-tesla-p100
```

```
gcloud beta container clusters create kubernetes-cluster \
  --machine-type n1-highmem-4 \
  --num-nodes 2 \
  --accelerator type=${ACCEL_TYPE},count=1 \
  --cluster-version 1.9.2-gke.1

```

**NOTE**: Do NOT try to beta create gpu clusters with an image
type, as this can prevent nvidia drivers (below) from installing properly. 

**Both CPU and GPU Clusters**: run the following to copy cluster info to your
local ~/.kube/config file, which enables `kubectl` command line to control
your cluster:

```
gcloud container clusters get-credentials kubernetes-cluster
```

Verify that everything is working using the `kubectl` command-line tool to see
that the Kubernetes Master is up and running: 

```
kubectl cluster-info
```

## Installing Nvidia Drivers

**GPU Cluster Only!**

Before you can make use of the GPU accelerators on your cluster, make sure to
follow these steps to setup your Nvidia cuda drivers on any containers that you
will deploy on GKE (Referenced from
[this page](https://cloud.google.com/kubernetes-engine/docs/concepts/gpus)):

Make sure your default kubectl context is
[pointing to your intended GKE cluster](KUBECTL_BASICS.md).

Next, add the GCP Nvidia Driver Daemon as a service to your cluster:
```
kubectl create -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/k8s-1.9/nvidia-driver-installer/cos/daemonset-preloaded.yaml
```

This will create a daemonset in your cluster under a
[namespace](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) 
`kube-system`. Check on the status of your nvidia-driver-installer by running:

```
kubectl get pods -n kube-system
```

You will see three pods like `nvidia-driver-installer-<some-hash>` in init
mode. Once they are running, you can proceed.

You are now ready to deploy GPU-enabled TF model serving containers!

