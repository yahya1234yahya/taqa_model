import os
import multiprocessing port = int(os.environ.get("PORT", 8080)) bind = f"0.0.0.0:{port}" print(f" Binding to {bind}") backlog = 2048 workers = 2 worker_

class = "sync" worker_connections = 1000 timeout = 300 keepalive = 2 max_requests = 500 max_requests_jitter = 50 accesslog = "-" errorlog = "-" loglevel = "info" capture_output = True proc_name = "equipment_api" daemon = False preload_app = True graceful_timeout = 120 worker_tmp_dir = "/tmp" threads = 1 worker_tmp_dir = "/tmp"