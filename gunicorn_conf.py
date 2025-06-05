# Gunicorn config file
import multiprocessing
import os

# Servidor y workers
bind = "unix:/tmp/llevateloexpress.sock"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
timeout = 60
keepalive = 2

# Logs
loglevel = "info"
accesslog = "/var/log/llevateloexpress/access.log"
errorlog = "/var/log/llevateloexpress/error.log"

# Seguridad y optimización
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30
limit_request_line = 4096
limit_request_fields = 100
