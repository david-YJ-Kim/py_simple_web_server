"""
Gunicorn 설정 파일 - Development 환경
개발 서버용 설정 (멀티 워커)
"""
import multiprocessing

# 바인딩 주소 및 포트
bind = "0.0.0.0:8000"

# 워커 설정
workers = multiprocessing.cpu_count() * 2 + 1  # CPU 코어 수 기반
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# 리로드 설정
reload = False  # Dev 서버에서는 리로드 비활성화 (안정성)
reload_engine = "auto"

# 타임아웃 설정
timeout = 120
keepalive = 5
graceful_timeout = 30

# 로깅 설정
accesslog = "logs/gunicorn.dev.access.log"
errorlog = "logs/gunicorn.dev.error.log"
loglevel = "info"

# 프로세스 이름
proc_name = "fastapi_app_dev"

# 기타 설정
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# 성능 최적화
max_requests = 1000
max_requests_jitter = 50

