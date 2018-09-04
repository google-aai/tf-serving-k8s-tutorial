#!/bin/bash
# This script creates a kubeflow deployment on GCP
# It checks for kubectl, gcloud, ks
# Uses default PROJECT, ZONE, EMAIL from gcloud config
# Creates a deployment manager config copy and edits appropriate values
# Creates the ksonnet app, installs packages, components and then applies them
#

# Go to your home directory
cd ~

# Install Kubeflow
KUBEFLOW_VERSION=0.2.2
KUBEFLOW_REPO=`pwd`/kubeflow_repo
KUBEFLOW_DEPLOY=true
KUBEFLOW_CLOUD="gke"
DEPLOYMENT_NAME=kubeflow

TAG=v${KUBEFLOW_VERSION}
TMPDIR=$(mktemp -d /tmp/tmp.kubeflow-repo-XXXX)
curl -L -o ${TMPDIR}/kubeflow.tar.gz https://github.com/kubeflow/kubeflow/archive/${TAG}.tar.gz
tar -xzvf ${TMPDIR}/kubeflow.tar.gz  -C ${TMPDIR}
# GitHub seems to strip out the v in the file name.
SOURCE_DIR=$(find ${TMPDIR} -maxdepth 1 -type d -name "kubeflow*")
mv ${SOURCE_DIR} "${KUBEFLOW_REPO}"

source "${KUBEFLOW_REPO}/scripts/util.sh"

KUBEFLOW_KS_DIR=`pwd`/${DEPLOYMENT_NAME}_ks_app

# Namespace where kubeflow is deployed. Just use default namespace to reduce confusion for students.
K8S_NAMESPACE=default

# Create the ksonnet app
cd $(dirname "${KUBEFLOW_KS_DIR}")
ks init $(basename "${KUBEFLOW_KS_DIR}")
cd "${KUBEFLOW_KS_DIR}"

ks env set default --namespace "${K8S_NAMESPACE}"
# Add the local registry
ks registry add kubeflow "${KUBEFLOW_REPO}/kubeflow"

# Install all required packages
ks pkg install kubeflow/tf-serving

# Generate all required components

ks generate tf-serving tf-serving

