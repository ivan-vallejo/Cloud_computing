#!/bin/bash

# 0. Connect to instance & get Anaconda
ssh -q -i $2 ec2-user@$1 << EOF
wget https://repo.continuum.io/archive/Anaconda2-5.1.0-Linux-x86_64.sh
# 1. Install Anaconda and configure it
bash Anaconda* -b -p ~/anaconda2
printf "\n export PATH=\"/home/ec2-user/anaconda2/bin:$PATH\"" >> /home/ec2-user/.bashrc
printf "\n source /home/ec2-user/anaconda2/bin/activate" >> /home/ec2-user/.bashrc
source /home/ec2-user/.bashrc
# 2. Set up jupyter notebook
jupyter notebook --generate-config
# IMPORTANT: hashcode to be replaced with the one for your personal password
# IMPORTANT: hashcode here corresponds to password "open_Internet"
printf "{\n\"NotebookApp\":{\n\"password\":\"sha1:011a9572479c:f01e766b3160b54dde4ab26c282c86a44fe5a0df\"\n}\n}" > /home/ec2-user/.jupyter/jupyter_notebook_config.json
# 3. Install emacs
sudo yes | sudo yum install emacs
EOF
