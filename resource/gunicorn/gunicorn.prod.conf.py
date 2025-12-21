"""
Gunicorn 설정 파일 - Production 환경
프로덕션 서버용 설정 (최적화)
"""
import multiprocessing
import os

# 바인딩 주소 및 포트
bind = "0.0.0.0:8000"

# 워커 설정
workers = multiprocessing.cpu_count() * 2 + 1  # CPU 코어 수 기반
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
threads = 2  # 워커당 스레드 수

# 리로드 설정 (프로덕션에서는 비활성화)
reload = False
preload_app = True  # 애플리케이션 사전 로드 (메모리 공유)

# 타임아웃 설정
timeout = 120
keepalive = 5
graceful_timeout = 30

# 로깅 설정
accesslog = "logs/gunicorn.prod.access.log"
errorlog = "logs/gunicorn.prod.error.log"
loglevel = "warning"  # 프로덕션에서는 warning 이상만 로깅

# 프로세스 이름
proc_name = "fastapi_app_prod"

# 기타 설정
daemon = False
pidfile = "logs/gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# 성능 최적화
max_requests = 1000
max_requests_jitter = 50

# 보안 설정
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

