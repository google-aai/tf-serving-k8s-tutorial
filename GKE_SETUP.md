# Google Kubernetes Engine Setup

Configure your gcloud settings first. If you need to, create a project
and set it as default. A preferred name (likely to be unique) would be
your gmail username followed by `-tf-serving-demo`, i.e. :
```
gcloud projects create <username>-tf-serving-demo --set-as-default
```

Select your default project:
```
PROJECT=$(gcloud config list --format 'value(core.project)')
```

Choose a zone to spin up your kubernetes cluster (e.g. `us-east1-c`):
```
ZONE=<your-zone>
```

Spin up a Kubernetes cluster in your preferred zone. You can change num-nodes to
any number of machines depending on how you'd like to scale your deployment, but
keep in mind that larger clusters require more cpu/gpu resources as the settings
are usually per node. Below we've defaulted to 3 node clusters.

If you want to use cpu only, run:

```
gcloud container clusters create kubernetes-cluster \
--scopes storage-rw \
--machine-type n1-standard-4 \
--num-nodes 3 \
--zone ${ZONE} \
--image-type UBUNTU
```

If you would like to run with GPU, you will have to use the gcloud beta mode.
Your accelerator type should be either `nvidia-tesla-k80` or
`nvidia-tesla-p100`. We explicitly set the gpu count to 2 as GKE will reserve
two gpus on the same board (Unfortunately, occasional errors occur when
requesting additional gpus...)

```
ACCEL_TYPE=nvidia-tesla-k80 | nvidia-tesla-p100
```

```
gcloud beta container clusters create kubernetes-cluster-gpu \
--accelerator type=${ACCEL_TYPE},count=2 \
--zone ${ZONE} \
--cluster-version 1.9.2-gke.1

```

**NOTE**: Do NOT try to beta create gpu clusters with a machine type or image
type, as this can prevent nvidia drivers (below) from installing properly. 

**NOTE #2**: Do

## Installing Nvidia Drivers

(For GPU only!)

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

