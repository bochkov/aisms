#!/bin/bash
set -e
source /home/bochkov/.virtualenvs/aisms/bin/activate
cd /home/bochkov/production/aisms_project
exec gunicorn -c gunicorn.conf.py aisms_project.wsgi:application
