"""
Gunicorn 설정 파일 - Local 환경
개발용 설정 (단일 워커, 리로드 가능)
"""
import multiprocessing

# 바인딩 주소 및 포트
# Docker 환경에서는 0.0.0.0으로 바인딩해야 외부 접근 가능
# 로컬 실행 시에는 127.0.0.1 사용 가능
bind = "0.0.0.0:8000"

# 워커 설정
workers = 1  # Local에서는 단일 워커
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# 리로드 설정 (개발용)
reload = True
reload_engine = "auto"

# 타임아웃 설정
timeout = 120
keepalive = 5
graceful_timeout = 30

# 로깅 설정
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "debug"

# 프로세스 이름
proc_name = "fastapi_app_local"

# 기타 설정
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

