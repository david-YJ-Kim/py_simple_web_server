from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError, OperationalError
import logging

from app.controller.sample_controller import sample_router
from app.controller.gn_rest_uri_path_controller import gn_rest_uri_path_router
from app.config import settings
from app.database.pos_neo.connection import init_db_pool, close_db_pool

# 모든 모델을 명시적으로 import하여 ForeignKey 관계가 정상 작동하도록 함
from app.database.pos_neo.models import GnRestUriDef, GnRestUriPath  # noqa: F401

# 로거 설정
logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.server.title,
    description=settings.server.description,
    version=settings.server.version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)

# add router
app.include_router(sample_router)
app.include_router(gn_rest_uri_path_router)


# ============================================
# 전역 예외 핸들러
# ============================================

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    SQLAlchemy 관련 예외 처리
    
    DB 조회 실패 시 애플리케이션이 중단되지 않고,
    적절한 HTTP 응답을 반환합니다.
    """
    logger.error(f"[DB Error] {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    # ProgrammingError: 테이블 없음, 컬럼 없음 등
    if isinstance(exc, ProgrammingError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database Error",
                "message": "데이터베이스 쿼리 실행 중 오류가 발생했습니다.",
                "detail": str(exc.orig) if hasattr(exc, 'orig') else str(exc)
            }
        )
    
    # OperationalError: 연결 실패, 타임아웃 등
    if isinstance(exc, OperationalError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "Database Connection Error",
                "message": "데이터베이스 연결에 실패했습니다.",
                "detail": str(exc.orig) if hasattr(exc, 'orig') else str(exc)
            }
        )
    
    # 기타 SQLAlchemy 예외
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "message": "데이터베이스 작업 중 오류가 발생했습니다.",
            "detail": str(exc)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    일반 예외 처리 (최종 안전망)
    
    처리되지 않은 모든 예외를 잡아서 애플리케이션이 중단되지 않도록 합니다.
    """
    logger.error(f"[Unhandled Error] {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "서버 내부 오류가 발생했습니다.",
            "detail": str(exc) if settings.server.debug else "서버 오류가 발생했습니다."
        }
    )

@app.on_event("startup")
async def startup_event():
    """ 서버 시작 시 실행되는 이벤트 """
    print(" 🚀 Start Web Server")
    print(f"config: {settings.__dict__}")
    
    # SQL 쿼리 로그 출력 설정
    if settings.database.echo_sql:
        # SQLAlchemy 엔진 로거 설정 (쿼리 로그 출력)
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        sqlalchemy_logger.setLevel(logging.INFO)
        print("✅ SQL 쿼리 로그 출력 활성화")
    
    # 데이터베이스 연결 풀 초기화
    try:
        await init_db_pool()
    except Exception as e:
        print(f"⚠️  데이터베이스 연결 실패: {e}")
        print("   서버는 계속 실행되지만 데이터베이스 기능은 사용할 수 없습니다.")


@app.on_event("shutdown")
async def shutdown_event():
    """ 서버 종료 시 실행되는 이벤트 """
    print(" 🛑 Shutting down Web Server")
    
    # 데이터베이스 연결 풀 종료
    await close_db_pool()



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload
    )