# Basic Kubectl Cheatsheet 

## Using Contexts

To check your contexts, run:

```
kubectl config get-contexts
```

The asterisk(*) should be next to the current context you are using.

To switch contexts, use a context name displayed by the `get-contexts` command:

```
kubectl config use-context <context-name>
```

## Creating Components

If you have a json or yaml file, run the following to create deployments and
services in your current context:

```
kubectl create -f <your-file>
```

## Scaling Up and Down

If you would like to change the number of pods deployed to your Kubernetes
cluster, you can [scale the deployment](https://kubernetes.io/docs/tasks/access-application-cluster/load-balance-access-application-cluster/):

Here is an example command:

```
kubectl scale deployment <your-deployment> --replicas=3
``` 

## Editing and Deleting Components

You list configurations of all [pods](https://kubernetes.io/docs/concepts/workloads/pods/pod/), 
[deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/),
and [services](https://kubernetes.io/docs/concepts/services-networking/service/)
by using the commands:

```
kubectl get deployments
```

```
kubectl get pods
```

```
kubectl get svc
```

To edit them (if you change the config, it will restart the component), use:

```
kubectl edit deployment <your-deployment>
```

```
kubectl edit pod <your-pod>
```

```
kubectl edit svc <your-service>
```

Likewise, you can delete by running `kubectl delete deployment/pod/svc <name>`.

If you delete a deployment, it will also kill all of the associated pods.

## Cleaning up

All of your kubectl cluster settings are located in your `~/.kube/config` file.
If you decided to remove a Kubernetes cluster for whatever reason, you can clean
up your kubectl environment by running:

```
kubectl config delete-context <context-name>
kubectl config delete-cluster <cluster-name>
```

You can verify that it is been removed by lookin at your `~/.kube/config` file.
