# Gunicorn config file
import multiprocessing
import os

# Servidor y workers - Configuración más conservadora
bind = "unix:/tmp/llevateloexpress.sock"
workers = max(2, multiprocessing.cpu_count())  # Máximo 4-8 workers en lugar de 9
worker_class = "sync"  # Cambiado de gevent a sync para evitar problemas de threading
worker_connections = 1000
timeout = 60
keepalive = 2

# Gestión de workers para evitar conexiones idle
max_requests = 500  # Reducido para forzar restart de workers
max_requests_jitter = 50
graceful_timeout = 30

# Logs
loglevel = "info"
accesslog = "/var/log/llevateloexpress/access.log"
errorlog = "/var/log/llevateloexpress/error.log"

# Seguridad y optimización
limit_request_line = 4096
limit_request_fields = 100

# Sin preload para evitar problemas de threading con DB
preload_app = False
