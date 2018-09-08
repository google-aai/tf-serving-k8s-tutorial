#!/bin/bash -eu
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Set up a simple VM with some basic python libraries and Jupyter to do
# estimator/keras work.
#
# Note: RUN THIS ON A COMPUTE ENGINE VM, not in the cloud shell!
#

#### Exit helper function ####
err() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $@" >&2
  exit 1
}

#### Bash variables ####
# The directory of the shell script, e.g. ~/code in the lecture slides.
BASE_DIR=$(dirname "$0")

#### APT-GET library installations ####

# Update apt-get
sudo apt-get update -y

# Install python3 and pip libraries
sudo apt-get install -y python-pip \
  python-dev \
  build-essential \
  || err 'failed to install python libraries'

#### Python Virtual Environment Setup ####

# Upgrade pip and virtual env
sudo pip install --upgrade pip
sudo pip install --upgrade virtualenv

# Create a virtual environment.
virtualenv -p python2 $HOME/env

# Create a function to activate environment in shell script.
activate () {
  . $HOME/env/bin/activate
}
activate || err 'failed to activate virtual env'

# Save activate command to bashrc so logging into the vm immediately starts env
# Remove any other commands in bashrc that is attempting to start a virtualenv
sed -i '/source.*\/bin\/activate/d' $HOME/.bashrc
echo 'source $HOME/env/bin/activate' >> $HOME/.bashrc

# Install requirements in the virtualenv
pip install -r $BASE_DIR/../client_requirements.txt \
  || err 'failed to pip install a required library'

# Add some env variables into your bashrc
echo 'Done with installation! Make sure to type: . ~/.bashrc to finish setup.'

#### DONE ####