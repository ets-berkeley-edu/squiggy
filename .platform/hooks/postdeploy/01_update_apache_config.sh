#!/bin/bash
sudo mv /tmp/ssl.conf /etc/httpd/conf.d/elasticbeanstalk/00_application.conf
sudo /bin/systemctl restart httpd.service
