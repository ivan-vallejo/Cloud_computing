#!/bin/bash

# 0. Connect to instance and run jupyter notebook on a detached screen
ssh -q -i $2 ec2-user@$1 << EOF
screen -d -m jupyter notebook --no-browser --port=8888
EOF
# 1. ssh to instance and reroute to localhost on a detached screen
if ! [ -x "$(command -v screen)" ]; then
  echo 'Script requires screen command. Please install it (e.g. apt-get install screen)' >&2
  return
fi
screen -d -m ssh -q -i $2 -L 8000:localhost:8888 ec2-user@$1
sleep 15
# 2. Open selected browser on localhost
export FONTCONFIG_PATH=/etc/fonts
$3&
