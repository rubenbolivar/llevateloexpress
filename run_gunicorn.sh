#!/bin/bash
cd /var/www/llevateloexpress
source backend_env/bin/activate
exec gunicorn -c gunicorn_conf.py llevateloexpress_backend.wsgi:application
