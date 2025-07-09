import multiprocessing bind = "0.0.0.0:5000" backlog = 2048 workers = multiprocessing.cpu_count() * 2 + 1 worker_

class = "sync" worker_connections = 1000 timeout = 300 keepalive = 2 max_requests = 1000 max_requests_jitter = 50 accesslog = "-" errorlog = "-" loglevel = "info" access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s' proc_name = "equipment_prediction_api" daemon = False pidfile = "/tmp/gunicorn.pid" tmp_upload_dir = None wsgi_module = "wsgi:
    app" preload_app = True graceful_timeout = 300 worker_tmp_dir = "/dev/shm"