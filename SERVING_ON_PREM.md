# Serving your model locally or on-prem

## Configuring access to your Jupyter Persistent Volumes

**This section is intended to be used after you have generated a servable model
with a Jupyter notebook spawned by JupyterHub.
Please do NOT run this section until you have saved a model into your
`work/tf-serving-k8s-tutorial/xxx-servable` directory!**

First, inside a terminal window, set the name of your user when you created your
notebook server in JupyterHub:

```
JUPYTER_USER=<your jupyterhub login name>
```

There should be a [pvc](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims)
with the name `claim-${JUPYTER_USER}` currently up. Verify this:

```
kubectl get pvc claim-${JUPYTER_USER}
```

Note that the claim points to a volume with a default 10Gi space. The volume
name should look something like `pvc-<some-hex-string-uuid>`. Copy the name
of your volume to a bash variable, and then check on its status:

```
JUPYTER_VOLUME=<your-volume-name>
```

```
kubectl get pv ${JUPYTER_VOLUME}
```

Under `ACCESS MODES`, you should see a `RWO`. This indicates that the volume
is using 'ReadWriteOnce' access, which allows only one pod (namely, your
Jupyter notebook server) to read and write from it. We are going to set this to
'ReadWriteMany' by modifying the pv. Run `kubectl edit` to open up the yaml
file containing the pv configurations:

```
kubectl edit pv ${JUPYTER_VOLUME}
```

In the yaml, there should be a section that looks like this:

```
spec:
  accessModes:
  - ReadWriteOnce
  capacity:
    storage: 10Gi
  claimRef:
  ...
```

Modify the `ReadWriteOnce` to `ReadWriteMany`, save, and exit. Your PV will be
patched to accept connections from multiple pods!

## Serve your Model

In a terminal, make sure that you are in your KubeFlow application directory:

```
cd ~/kubeflow_ks_app
```

You will need to run a set of configurations to serve from your PV. First,
let's configure the parameters that are agnostic to your cluster, based on the
names used to build your model. We will be using TF Serving 1.8 CPU first to
validate (guidelines for deploying serving with GPU is further below). First,
set your shell variable `MODEL_TYPE` to either `estimator` or `keras`, depending
on the servable model you packaged and saved.

```
MODEL_TYPE = <estimator | keras>
```

Now, set the following parameters for your serving app `my-tf-serving`:
```
ks param set my-tf-serving name my-tf-serving
ks param set my-tf-serving numGpus 0
ks param set my-tf-serving modelName resnet
ks param set my-tf-serving modelPath /mnt/work/tf-serving-k8s-tutorial/jupyter/${MODEL_TYPE}_servable/
ks param set my-tf-serving defaultCpuImage "gcr.io/kubeflow-images-public/tensorflow-serving-1.8@sha256:a6ffaa593939fce62fd9babc6c6c7539c40e9bf48deeb290e9ae3ef756453336"
```

Note that the directory `/mnt/` will need to point to your Jupyter server's home
folder in order for the `modelPath` to work correctly. In order to do this,
we will configure your storage based on your PV. By default, TF serving
will serve locally, or if the modelPath contains certain prefixes, e.g. "s3://"
or "gs://", it will use the cloud provider's storage granted that your cloud
credentials are correctly set. Since we will be serving directly from the PV,
we need to explicitly specify network file system (nfs) as the storage type,
and assign a PVC for our serving app to access the PV
```
ks param set my-tf-serving modelStorageType nfs
ks param set my-tf-serving nfsPVC claim-${JUPYTER_USER}
```

Finally, run the following to deploy your model serving application:
```
ks apply default -c my-tf-serving
```

If all goes well, you should see the my-tf-serving pod in 'running' state after
a minute or so:

```
SERVING_POD=`kubectl get pods --selector="app=my-tf-serving" --output=template --template="{{with index .items 0}}{{.metadata.name}}{{end}}"`
kubectl get pods ${SERVING_POD}
```

[Proceed to the TF Client section](README.md#tf-client)
 to continue with using a client to access your server!

**Troubleshooting**: [see here](TROUBLESHOOTING.md#tensorflow-serving).

## GPU Serving Configurations

Prerequisite: Make sure that you have an NVIDIA-driver installed for your
k8s cluster.

To add GPUs for serving, you will need to add/modify a couple parameters:

```
ks param set my-tf-serving numGpus 1
ks param set my-tf-serving defaultGpuImage "gcr.io/kubeflow-images-public/tensorflow-serving-1.8gpu@sha256:03c6634cdb17643f17f7302f92e8b48216d97685850086631054414de89a4246"
```

Then reapply the changes:

```
ks apply default -c my-tf-serving
```

**Note:** if you want to use any other version of TensorFlow Serving for CPU or
GPU, an exhaustive list of KubeFlow provided images can be found here:

```
https://console.cloud.google.com/gcr/images/kubeflow-images-public/GLOBAL
```
