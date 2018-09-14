# Troubleshooting manual

## KubeFlow Install

**Issue:** KubeFlow failed to install due to a missing dependency!

**Answer:** Install that dependency, remove the
KubeFlow app directory, and run installation/deployment again:

```
cd ~
rm -rf ~/kubeflow_ks_app/
curl https://raw.githubusercontent.com/kubeflow/kubeflow/v0.2.5/scripts/deploy.sh | bash
```

**Issue:**  My minikube is really slow to deploy kubeflow pods!
 
**Answer:** If you do not have a powerful local computer and notice
minikube draining power or taking a long time to deploy pods, for this tutorial
you actually do not need anything from the default KubeFlow environment except
the tf-hub-0 pod in KubeFlow, which is not tied to any deployment. Run:
```
for i in $(kubectl get deployment | tail -n +2 | cut -d' ' -f1); do
  kubectl delete deployment $i
done
```

Now run: 
```
kubectl get pods
```

You should some pods terminating, with only a single pod tf-hub-0 running.

**Issue:** I needed to recreate my cluster, and trying to run
`ks apply default -c kubeflow-core` now returns:

```
ERROR Attempting to deploy to environment 'default' at '<some address>', but cannot locate a server at that address
```

**Answer:** KubeFlow is still pointing to your old cluster address! Run:
```
kubectl describe svc kubernetes
```
and note the `address:port` under `EndPoints:`. Open up the app.yaml file in
your kubeflow_ks_app directory, and edit the server under environment -> default
to point to this new `address:port`. Then rerun:

`ks apply default -c kubeflow-core`

## TensorFlow Serving

**Issue**: My pod is not running or is crashing!

**Answer:** If your pod fails to run, you can use
`kubectl describe pod ${SERVING_POD}` to check on what went wrong. Sometimes,
it will show that the PV can not be mounted, or the image could not be found
(wrong path or bucket),
or there were insufficient resources. If you are running locally, cpu may
be a likely issue if you allocated too many cpus to your Jupyter notebook.
One way to free up your resources is to shut down some running pods, such as
your notebook pod. To do so, go to your notebook and click `logout`. Next,
delete your pod from k8s:

```
kubectl delete pod jupyter-${JUPYTER_USER}
```

If you wish to startup your Jupyter environment again, you can go back to 
`localhost:8000` and spawn a new environment with the same user name/password,
and it will spawn a new pod that can access the same PV.

Another command that is helpful to verify that the model is reachable is:

```
kubectl logs ${SERVING_POD}
```
