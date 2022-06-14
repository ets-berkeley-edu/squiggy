#!/bin/bash

sudo curl -sL https://rpm.nodesource.com/setup_14.x | sudo bash -
sudo yum install -y nodejs
sudo npm install -g typescript
sudo npm install -g fabric

sudo pip3 install -g eventlet==0.33.1

exit 0
