# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5 minutes for ML model loading
keepalive = 2

# Restart workers after this many requests, to avoid memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "equipment_prediction_api"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
tmp_upload_dir = None

# SSL (if needed later)
# keyfile = None
# certfile = None

# Application
wsgi_module = "wsgi:app"

# Preload application for better memory usage
preload_app = True

# Worker timeout for model loading
graceful_timeout = 300
worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files 