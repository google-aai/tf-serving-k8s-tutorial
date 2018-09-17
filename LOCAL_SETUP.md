# Setting up your Local Kubernetes Environment

* Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): to create
and manage your cluster (deployments, services, scaling, etc)
* Installing a type-2 hypervisor such as
[VirtualBox](www.virtualbox.org) and a hypervisor driver such as
[xhyve](https://github.com/mist64/xhyve).
* [Install Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)
on your local machine.

## Setup Minikube

In order to run KubeFlow on Minikube, make sure that your computer has at least
4 cpus, preferably 16Gb memory, and over 40g disk space. Then start Minikube
with your driver specified:
```
minikube start --cpus 4 --memory 8096 --disk-size=40g --vm-driver <your-driver>
```

Optionally, you can also specify a hypervisor to use on the command line if you
decided to use a hypervisor to run minikube based on your setup step.

Check that minikube is registered in your kubectl cluster info:
```
kubectl config get-contexts
```

You can also check the cluster info for minikube and ensure that your cluster
is up and running:
```
kubectl cluster-info
```

If all goes well, congratulations! You're ready to start a local
deployment of TF model serving!

**Troubleshooting:** See [here](TROUBLESHOOTING.md#kubeflow-install).

