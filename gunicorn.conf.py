# gunicorn配置文件
bind = "0.0.0.0"
workers = 1
worker_class = "eventlet"
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True