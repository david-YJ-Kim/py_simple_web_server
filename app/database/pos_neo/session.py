"""
SQLAlchemy 비동기 세션 관리 모듈

Spring Boot의 @Transactional과 유사한 역할을 합니다.

connection 과 달리 별도 풀을 생성해서 관리.
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from typing import AsyncGenerator, Optional
from app.config import settings


# SQLAlchemy 비동기 엔진
_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    """
    SQLAlchemy 비동기 엔진 생성 및 반환
    
    Returns:
        AsyncEngine: SQLAlchemy 비동기 엔진
    """
    global _engine
    
    if _engine is None:
        # PostgreSQL asyncpg 드라이버 사용
        database_url = (
            f"postgresql+asyncpg://{settings.database.user}:{settings.database.password}"
            f"@{settings.database.host}:{settings.database.port}/{settings.database.name}"
        )
        
        # SSL 설정
        connect_args = {}
        if settings.database.ssl_mode and settings.database.ssl_mode.lower() == "require":
            connect_args["ssl"] = "require"
        
        _engine = create_async_engine(
            database_url,
            echo=settings.database.echo_sql,  # SQL 쿼리 로깅 (config.yaml에서 설정)
            pool_pre_ping=True,  # 연결 유효성 검사
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            connect_args=connect_args
        )
        
        print(f"✅ SQLAlchemy 비동기 엔진 생성 완료")
    
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    비동기 세션 팩토리 생성 및 반환
    
    Returns:
        async_sessionmaker: 비동기 세션 팩토리
    """
    global _async_session_factory
    
    if _async_session_factory is None:
        engine = get_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # 커밋 후 객체 만료 방지
            autoflush=False,  # 자동 flush 비활성화 (명시적 제어)
            autocommit=False  # 자동 커밋 비활성화
        )
    
    return _async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency로 사용할 수 있는 세션 생성기
    
    Spring Boot의 @Transactional과 유사한 역할
    
    사용 예시:
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_db_session)):
            repo = UserRepository(session)
            users = await repo.find_all()
            return users
    
    Yields:
        AsyncSession: SQLAlchemy 비동기 세션
    """
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        try:
            yield session
            await session.commit()  # 성공 시 커밋
        except Exception:
            await session.rollback()  # 실패 시 롤백
            raise
        finally:
            await session.close()


async def close_engine() -> None:
    """
    엔진 종료 (애플리케이션 종료 시 호출)
    """
    global _engine
    
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        print("✅ SQLAlchemy 엔진 종료 완료")

