# Gunicorn configuration for DigitalOcean App Platform
import os
import multiprocessing

# Server socket - App Platform sets PORT automatically
port = int(os.environ.get("PORT", 8080))  # App Platform default is 8080
bind = f"0.0.0.0:{port}"
print(f"🌐 Binding to {bind}")
backlog = 2048

# Worker processes - Conservative for App Platform
workers = 2  # App Platform has limited resources on basic plans
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5 minutes for ML model loading
keepalive = 2

# Memory management for App Platform
max_requests = 500  # Restart workers more frequently to manage memory
max_requests_jitter = 50

# Logging - App Platform captures these
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True

# Process naming
proc_name = "equipment_api"

# Server mechanics
daemon = False
preload_app = True  # Important for faster startup

# Timeouts for App Platform
graceful_timeout = 120
worker_tmp_dir = "/tmp"

# Optimize for App Platform resources
threads = 1
worker_tmp_dir = "/tmp" 