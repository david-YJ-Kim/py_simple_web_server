@echo off
REM Local 환경 실행 스크립트 (Windows)
REM Uvicorn을 사용하여 애플리케이션을 실행합니다.
REM .env 파일에서 ENV 설정을 읽어옵니다.

REM ========================================
REM Gunicorn을 사용하지 않는 이유:
REM ========================================
REM 1. Gunicorn은 Unix/Linux 전용으로 설계되어 Windows에서 실행 불가
REM 2. fcntl 모듈이 Unix/Linux 전용이므로 Windows에서 ModuleNotFoundError 발생
REM 3. Windows 프로덕션 환경에서는 Waitress 또는 Docker 사용 권장
REM 4. Local 개발 환경에서는 Uvicorn이 더 적합 (자동 리로드 지원)
REM ========================================

REM 프로젝트 루트로 이동
cd /d "%~dp0\.."

REM Uvicorn 실행
REM .env 파일의 ENV 설정에 따라 자동으로 적절한 config.yaml 파일 사용
echo 🚀 Starting FastAPI application (Local environment)...
echo 📝 Note: ENV is read from .env file
echo 📝 Server: Uvicorn (Windows compatible)
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause

