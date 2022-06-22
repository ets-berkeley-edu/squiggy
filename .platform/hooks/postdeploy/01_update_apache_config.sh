#!/bin/bash

sudo mv /tmp/web_sockets.conf /etc/httpd/conf.d/elasticbeanstalk/00_application.conf
sudo /bin/systemctl restart httpd.service

exit 0
