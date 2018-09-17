# Serving your model on GKE

To serve on Google K8s Engine, you can also follow the instructions for 
[serving on-prem](SERVING_ON_PREM.md), since the configuration is general enough
to support minikube as well as most cluster configurations. However, if you're
using Google Cloud, why not take advantage of cloud resources?

## Export your model to Google Storage

If you are running KubeFlow on Google Cloud Platform, you can serve the model
after exporting it to google storage. Exporting to google storage has not only
the benefit of virtually unlimited storage space, but it can allow you
to provide more fine-grained access control of your model to other users,
projects, and K8s clusters. (By default, your cluster should have access to your
model.)

Run the commands in the
`export_model_gcp.ipynb` notebook to create a Google storage bucket in your
project, and export your model to a bucket.

## Serve your model

First,
set your shell variable `MODEL_TYPE` to either `estimator` or `keras`, depending
on the servable model you packaged and saved.

```
MODEL_TYPE = <estimator | keras>
```

Next, let's find your model on Google storage. If you have the gcloud command
line tool installed and are switched to the appropriate project, run:

```
PROJECT=<your project name>
```

and then

```
BUCKET=${PROJECT}-bucket
```

Configure your `my-tf-serving` app to use TF 1.8 CPU to serve a model by
pointing to the directory in your Google storage bucket:


```
ks param set my-tf-serving name my-tf-serving
ks param set my-tf-serving numGpus 0
ks param set my-tf-serving modelName resnet
ks param set my-tf-serving modelPath gs://${BUCKET}/${MODEL_TYPE}_servable/
ks param set my-tf-serving defaultCpuImage "gcr.io/kubeflow-images-public/tensorflow-serving-1.8@sha256:a6ffaa593939fce62fd9babc6c6c7539c40e9bf48deeb290e9ae3ef756453336"
```

Once you are done setting your parameters, deploy your application:

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

**Troubleshooting:** [see here](TROUBLESHOOTING.md#tensorflow-serving).

## GPU Serving Configurations

If you have a GKE cluster with GPUs, you will need to follow instructions to
enable GPUs. You can go [here](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus)
for the full documentation, but essentially if you already have a cluster up
and running and kubectl linked to the cluster, you simply need to run a
daemonset to install device plugins for your GPU:

```
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/stable/nvidia-driver-installer/cos/daemonset-preloaded.yaml
```

Then, [follow the instructions here](SERVING_ON_PREM.md#gpu-serving-configurations)
to setup KubeFlow TensorFlow serving to use GPUs.