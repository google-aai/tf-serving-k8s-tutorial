# How to Contribute

This repository is meant as a basic tutorial for Tensorflow Serving deployment
on Kubernetes. If you would like to contribute to other solutions around the
deployment of Tensorflow Serving, we encourage you to contribute to the
[Kubeflow](https://github.com/kubeflow/kubeflow) project.

For the purpose of improving this tutorial, we'd love to accept contributions to
this project if it improves clarity or demonstrates an updated approach to
deploying TF serving. There are a few small guidelines you need to follow. 

## Contributor License Agreement

Contributions to this project must be accompanied by a Contributor License
Agreement. You (or your employer) retain the copyright to your contribution,
this simply gives us permission to use and redistribute your contributions as
part of the project. Head over to <https://cla.developers.google.com/> to see
your current agreements on file or to sign a new one.

You generally only need to submit a CLA once, so if you've already submitted one
(even if it was for a different project), you probably don't need to do it
again.

## Code reviews

All submissions, including submissions by project members, require review. We
use GitHub pull requests for this purpose. Consult
[GitHub Help](https://help.github.com/articles/about-pull-requests/) for more
information on using pull requests.

## Notebooks

For notebook contributions or edits, after making proper changes, please shut
down your notebook editor (e.g. Jupyter, Colab, etc.), and run the python script
in the project's base directory as the FINAL STEP to ensure that outputs and
other editor-specific metadata are removed. This ensures that diffs between
notebooks are clearly marked during code review.

```
python cleanup_notebooks.py
```
