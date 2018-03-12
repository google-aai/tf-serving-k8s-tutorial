# Setting up your Local Kubernetes Environment

[Install Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)
on your local machine. Note that this will require installing a type-2
hypervisor such as [VirtualBox](www.virtualbox.org) and a hypervisor driver such
as [xhyve](https://github.com/mist64/xhyve). **The below instructions assume we
are using VirtualBox and xhyve, but you are free to use other virtualization
solutions.**

## Additional Setup Steps

You will also need to download and install the following:

* [Docker](https://www.docker.com/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): to create
and manage your cluster (deployments, services, scaling, etc)

## Spin up a Docker machine

(For local deployments only!)

Start a docker machine on virtualbox and setup its environment:

```
docker-machine create --driver virtualbox default
eval $(docker-machine env default)
```

Check that the machine has a valid ip:

```
docker-machine ip
```

## Setup Minikube for Docker Access

Run these commands to ensure that minikube is running and that it has access
to your local docker image repository.
```
minikube start --vm-driver=xhyve
eval $(minikube docker-env)
```

Now follow the steps at the bottom of this page to create a docker registry:
https://blog.hasura.io/sharing-a-local-registry-for-minikube-37c7240d0615

Note: if you're using a Mac, you might discover that you will have to allow
127.0.0.1:5000 as an insecure registry in your docker machine.
([Source](https://stackoverflow.com/questions/32808215/where-to-set-the-insecure-registry-flag-on-mac-os))
To do this, ssh into your docker machine:

```
ssh -i ~/.docker/machine/machines/default/id_rsa -R 5000:localhost:5000 docker@$(docker-machine ip)
```

Then edit the file `/var/lib/boot2docker/profile`, and modify the snippet:

```
EXTRA_ARGS='
--label provider=virtualbox --insecure-registry 127.0.0.1:5000

'
```

Then reboot the docker machine and exit
```
sudo /etc/init.d/docker restart
exit
```

Once you're done with the steps, run the ssh command (again) to enable port
forwarding.

```
ssh -i ~/.docker/machine/machines/default/id_rsa -R 5000:localhost:5000 docker@$(docker-machine ip)
```

Open another shell and continue.

Check that minikube is registered in your kubectl cluster info:
```
kubectl config get-contexts
```

If minikube shows up here, congratulations! You're ready to start a local
deployment of TF model serving!