from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controller.sample_controller import sample_router
from app.config import settings
from app.database.connection import init_db_pool, close_db_pool


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

@app.on_event("startup")
async def startup_event():
    """ 서버 시작 시 실행되는 이벤트 """
    print(" 🚀 Start Web Server")
    print(f"config: {settings.__dict__}")
    
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