#!/bin/bash
sudo gunicorn -k gevent -w 1 squiggy:app
