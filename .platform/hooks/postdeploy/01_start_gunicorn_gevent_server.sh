#!/bin/bash

source "${PYTHONPATH}/activate"
gunicorn -k gevent -w 1 squiggy:app
