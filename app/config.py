"""
애플리케이션 설정 관리 모듈

환경 변수(.env)와 YAML 설정 파일을 로드하여 통합 관리합니다.
"""
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


# .env 파일 로드 (환경 변수를 먼저 로드해야 ENV를 읽을 수 있음)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ .env 파일 로드 완료: {env_path}")
    # 디버깅: DB_PASSWORD 환경 변수 확인 (보안상 값은 표시하지 않음)
    db_password = os.getenv("DB_PASSWORD")
    if db_password:
        print(f"   - DB_PASSWORD: {'*' * len(db_password)} (길이: {len(db_password)})")
    else:
        print(f"   ⚠️  DB_PASSWORD 환경 변수가 설정되지 않았습니다.")
else:
    print(f"⚠️  .env 파일을 찾을 수 없습니다: {env_path}")


class ServerSettings(BaseSettings):
    """서버 관련 설정"""
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    debug: bool = Field(default=True)
    reload: bool = Field(default=True)
    title: str = "Simple Web Server w/ FastAPI"
    description: str = "Simple Web Server w/ FastAPI"
    version: str = "0.0.1"


class CORSSettings(BaseSettings):
    """CORS 관련 설정"""
    allow_origins: List[str] = Field(default=["*"])
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]


class LoggingSettings(BaseSettings):
    """로깅 관련 설정"""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = Field(default=None, env="LOG_FILE")
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5


class DatabaseSettings(BaseSettings):
    """데이터베이스 관련 설정"""
    host: str = Field(default="localhost")  # YAML에서만 가져옴 (env 제거)
    port: int = Field(default=5432)  # YAML에서만 가져옴 (env 제거)
    name: str = Field(default="myapp")  # YAML에서만 가져옴 (env 제거)
    user: str = Field(default="user")  # YAML에서만 가져옴 (env 제거)
    password: str = Field(default="password", env="DB_PASSWORD")  # 환경 변수에서만 가져옴
    ssl_mode: Optional[str] = Field(default=None)  # SSL 모드 (require, prefer, disable 등)
    pool_size: int = 10
    max_overflow: int = 20


class APISettings(BaseSettings):
    """API 관련 설정"""
    timeout: int = 30
    retry_count: int = 3
    rate_limit: int = 100


class Settings:
    """통합 설정 클래스"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        설정 초기화
        
        환경 변수 ENV에 따라 적절한 설정 파일을 자동으로 선택하여 로드합니다.
        
        동작 과정:
        1. 환경 변수 ENV 확인 (기본값: local)
        2. resource/conf/config.{ENV}.yaml 파일 경로 설정
        3. YAML 파일 읽기 → Python 딕셔너리로 변환
        4. 딕셔너리 데이터를 각 Settings 클래스에 전달
        5. 환경 변수(.env)가 있으면 우선 적용
        
        Args:
            config_file: YAML 설정 파일 경로 (지정하지 않으면 ENV에 따라 자동 선택)
        """
        # 1단계: 환경 변수 ENV 확인 (기본값: local)
        env = os.getenv("ENV", "local").lower()
        
        # 2단계: YAML 파일 경로 설정
        # config_file이 지정되지 않았으면 환경별 파일 자동 선택
        if config_file is None:
            conf_dir = Path(__file__).parent.parent / "resource" / "conf"
            if env == "local":
                config_file = conf_dir / "config.yaml"
            else:
                config_file = conf_dir / f"config.{env}.yaml"
            
            # 파일이 없으면 기본 config.yaml 사용
            if not config_file.exists() and env != "local":
                config_file = conf_dir / "config.yaml"
        else:
            config_file = Path(config_file)
        
        # 3단계: YAML 파일 읽기 및 파싱
        # config.yaml 파일을 읽어서 Python 딕셔너리로 변환합니다
        # 예: {"server": {"host": "127.0.0.1", "port": 8000}, ...}
        yaml_config = {}
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f) or {}
        
        # 4단계: 딕셔너리 데이터를 Python 객체로 변환
        # yaml_config.get("server", {}) → {"host": "127.0.0.1", "port": 8000}
        # ServerSettings(**{...}) → ServerSettings 객체 생성
        # 주의: Pydantic BaseSettings는 kwargs가 환경 변수보다 우선하므로,
        # 환경 변수를 우선시하려면 YAML에서 보안 정보(비밀번호 등)를 제외해야 합니다.
        
        # YAML에서 database 설정 가져오기 (password 제외 - 환경 변수에서만 가져옴)
        db_config = yaml_config.get("database", {}).copy()
        # password는 YAML에서 제거하여 환경 변수(.env)에서만 가져오도록 함
        # 보안상 비밀번호는 반드시 환경 변수로만 관리
        db_config.pop("password", None)
        
        self.server = ServerSettings(**yaml_config.get("server", {}))
        self.cors = CORSSettings(**yaml_config.get("cors", {}))
        self.logging = LoggingSettings(**yaml_config.get("logging", {}))
        
        # DatabaseSettings 생성: kwargs를 전달하지 않고 환경 변수에서만 읽도록 함
        # Pydantic BaseSettings는 kwargs가 있으면 환경 변수를 무시하므로,
        # password는 kwargs에서 제외하고 환경 변수에서만 읽어야 함
        self.database = DatabaseSettings(**db_config)  # password 제외된 설정 사용
        
        # password가 기본값이면 환경 변수에서 직접 설정
        if self.database.password == "password" or not self.database.password:
            env_password = os.getenv("DB_PASSWORD")
            if env_password:
                # Pydantic 모델의 필드를 직접 업데이트
                self.database.password = env_password
                print(f"✅ 환경 변수에서 password 로드 완료: {'*' * len(env_password)} (길이: {len(env_password)})")
            else:
                print(f"⚠️  DB_PASSWORD 환경 변수가 설정되지 않았습니다.")
        
        # 디버깅: DatabaseSettings 생성 후 password 확인
        db_password_loaded = self.database.password
        if db_password_loaded and db_password_loaded != "password":  # 기본값이 아닌 경우
            print(f"✅ DatabaseSettings.password 최종 확인: {'*' * len(db_password_loaded)} (길이: {len(db_password_loaded)})")
        else:
            print(f"⚠️  DatabaseSettings.password가 기본값입니다. 환경 변수 DB_PASSWORD를 확인하세요.")
            print(f"   - 현재 값: {db_password_loaded}")
            print(f"   - 환경 변수 DB_PASSWORD: {os.getenv('DB_PASSWORD', '(없음)')}")
        
        self.api = APISettings(**yaml_config.get("api", {}))
        
        # CORS allow_origins 문자열 파싱 (환경 변수에서)
        if isinstance(self.cors.allow_origins, str):
            self.cors.allow_origins = [
                origin.strip() 
                for origin in self.cors.allow_origins.split(",")
            ]
    
    def get_database_url(self) -> str:
        """데이터베이스 연결 URL 생성"""
        return (
            f"postgresql://{self.database.user}:{self.database.password}"
            f"@{self.database.host}:{self.database.port}/{self.database.name}"
        )


# 전역 설정 인스턴스
settings = Settings()


# 사용 예제:
# from app.config import settings
# print(settings.server.host)
# print(settings.database.host)

