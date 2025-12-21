# Python 3.11 기반 이미지
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY app/ ./app/

# 설정 파일 복사 (YAML 파일만 - 보안 정보 제외)
COPY resource/conf/ ./resource/conf/
COPY resource/gunicorn/ ./resource/gunicorn/

# 로그 디렉토리 생성
RUN mkdir -p logs

# 포트 노출
EXPOSE 8000

# 환경 변수 설정 (기본값)
ENV ENV=prod
ENV PYTHONUNBUFFERED=1

# Gunicorn 실행
# 환경 변수 ENV에 따라 적절한 Gunicorn 설정 파일 사용
# ENV가 없으면 기본값 prod 사용
CMD ["sh", "-c", "if [ -z \"$ENV\" ]; then ENV=prod; fi && gunicorn app.main:app -c resource/gunicorn/gunicorn.${ENV}.conf.py"]

