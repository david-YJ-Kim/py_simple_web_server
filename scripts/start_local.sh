#!/bin/bash

# Local 환경 실행 스크립트
# Gunicorn을 사용하여 애플리케이션을 실행합니다.
# .env 파일에서 ENV 설정을 읽어옵니다.

# 설정 파일 경로
CONFIG_FILE="resource/gunicorn/gunicorn.local.conf.py"

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.." || exit

# Gunicorn 실행
echo "🚀 Starting FastAPI application..."
echo "📁 Config: $CONFIG_FILE"
echo "📝 Note: ENV is read from .env file"
echo ""

gunicorn app.main:app -c "$CONFIG_FILE"

