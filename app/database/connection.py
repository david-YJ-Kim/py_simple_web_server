"""
PostgreSQL 데이터베이스 연결 풀 관리 모듈

이 모듈은 asyncpg를 사용하여 PostgreSQL 데이터베이스와의 연결을 관리합니다.
연결 풀을 사용하여 효율적으로 데이터베이스 연결을 재사용합니다.
"""
import asyncpg
from typing import Optional
from app.config import settings


# 전역 연결 풀 변수
_db_pool: Optional[asyncpg.Pool] = None


async def init_db_pool() -> asyncpg.Pool:
    """
    데이터베이스 연결 풀 초기화
    
    애플리케이션 시작 시 한 번 호출하여 연결 풀을 생성합니다.
    config.py의 DatabaseSettings에서 설정값을 가져옵니다.
    
    Returns:
        asyncpg.Pool: 생성된 연결 풀 객체
        
    Raises:
        asyncpg.PostgresError: 데이터베이스 연결 실패 시
    """
    global _db_pool
    
    if _db_pool is not None:
        return _db_pool
    
    try:
        # 연결 풀 생성
        # min_size: 최소 연결 수 (기본값: 10)
        # max_size: 최대 연결 수 (기본값: 10)
        # max_queries: 연결당 최대 쿼리 수 (기본값: 50000)
        # max_inactive_connection_lifetime: 비활성 연결 유지 시간 (초)
        _db_pool = await asyncpg.create_pool(
            host=settings.database.host,
            port=settings.database.port,
            user=settings.database.user,
            password=settings.database.password,
            database=settings.database.name,
            min_size=1,  # 최소 연결 수
            max_size=settings.database.pool_size,  # 최대 연결 수 (config에서 가져옴)
            max_queries=50000,  # 연결당 최대 쿼리 수
            max_inactive_connection_lifetime=300,  # 5분간 비활성 연결 유지
            command_timeout=60,  # 쿼리 타임아웃 (초)
        )
        
        print(f"✅ PostgreSQL 연결 풀 생성 완료")
        print(f"   - Host: {settings.database.host}:{settings.database.port}")
        print(f"   - Database: {settings.database.name}")
        print(f"   - User: {settings.database.user}")
        print(f"   - Pool Size: {settings.database.pool_size}")
        
        return _db_pool
        
    except asyncpg.PostgresError as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
        raise
    except Exception as e:
        print(f"❌ 데이터베이스 연결 풀 생성 중 오류 발생: {e}")
        raise


async def close_db_pool() -> None:
    """
    데이터베이스 연결 풀 종료
    
    애플리케이션 종료 시 호출하여 모든 연결을 정리합니다.
    """
    global _db_pool
    
    if _db_pool is not None:
        await _db_pool.close()
        _db_pool = None
        print("✅ PostgreSQL 연결 풀 종료 완료")


def get_db_pool() -> Optional[asyncpg.Pool]:
    """
    현재 생성된 연결 풀을 반환합니다.
    
    Returns:
        Optional[asyncpg.Pool]: 연결 풀이 생성되어 있으면 Pool 객체, 없으면 None
    """
    return _db_pool


async def get_connection():
    """
    연결 풀에서 연결을 가져옵니다.
    
    이 함수는 async context manager로 사용할 수 있습니다:
    
    Example:
        async with get_connection() as conn:
            result = await conn.fetch("SELECT * FROM users")
    
    Returns:
        asyncpg.Connection: 데이터베이스 연결 객체
        
    Raises:
        RuntimeError: 연결 풀이 초기화되지 않은 경우
    """
    pool = get_db_pool()
    
    if pool is None:
        raise RuntimeError(
            "데이터베이스 연결 풀이 초기화되지 않았습니다. "
            "먼저 init_db_pool()을 호출하세요."
        )
    
    return pool.acquire()


# 편의 함수: 연결 풀을 직접 사용하는 방법
async def execute_query(query: str, *args) -> list:
    """
    쿼리를 실행하고 결과를 반환합니다.
    
    Args:
        query: 실행할 SQL 쿼리
        *args: 쿼리 파라미터
        
    Returns:
        list: 쿼리 결과 리스트
        
    Example:
        results = await execute_query("SELECT * FROM users WHERE id = $1", user_id)
    """
    pool = get_db_pool()
    
    if pool is None:
        raise RuntimeError("데이터베이스 연결 풀이 초기화되지 않았습니다.")
    
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def execute_insert(query: str, *args) -> str:
    """
    INSERT 쿼리를 실행하고 삽입된 행의 ID를 반환합니다.
    
    Args:
        query: 실행할 INSERT SQL 쿼리 (RETURNING id 포함 권장)
        *args: 쿼리 파라미터
        
    Returns:
        str: 삽입된 행의 ID (RETURNING 절이 있는 경우)
        
    Example:
        user_id = await execute_insert(
            "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id",
            "홍길동", "hong@example.com"
        )
    """
    pool = get_db_pool()
    
    if pool is None:
        raise RuntimeError("데이터베이스 연결 풀이 초기화되지 않았습니다.")
    
    async with pool.acquire() as conn:
        result = await conn.fetchrow(query, *args)
        if result:
            # RETURNING 절이 있는 경우 첫 번째 컬럼 반환
            return result[0] if len(result) > 0 else None
        return None

