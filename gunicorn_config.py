"""
Gunicorn konfigurácia pre produkčné nasadenie
"""

import multiprocessing
import os

# Server socket
bind = f"127.0.0.1:{os.getenv('PORT', '6002')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "logs/gunicorn-access.log"
errorlog = "logs/gunicorn-error.log"
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "vps-dashboard-api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (ak používaš SSL priamo v Gunicorn)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Performance
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Graceful timeout
graceful_timeout = 30

# Speciálne nastavenia pre Flask
def on_starting(server):
    """Volané pri štarte servera"""
    server.log.info("🚀 VPS Dashboard API starting...")

def on_reload(server):
    """Volané pri reload"""
    server.log.info("🔄 VPS Dashboard API reloading...")

def worker_int(worker):
    """Volané pri prerušení worker procesu"""
    worker.log.info("⚠️ Worker interrupted")

def pre_fork(server, worker):
    """Volané pred fork worker procesu"""
    pass

def post_fork(server, worker):
    """Volané po fork worker procesu"""
    server.log.info(f"✅ Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    """Volané po inicializácii worker procesu"""
    worker.log.info("✅ Worker initialized")

def worker_abort(worker):
    """Volané pri abort worker procesu"""
    worker.log.error("❌ Worker aborted")

