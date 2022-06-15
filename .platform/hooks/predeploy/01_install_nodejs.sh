#!/bin/bash

sudo curl -sL https://rpm.nodesource.com/setup_14.x | sudo bash -
sudo yum install -y nodejs
sudo npm install -g typescript
sudo npm install -g fabric

exit 0
