"""
Service Dependency Injection 모듈

FastAPI의 Dependency Injection을 사용하여 Service를 싱글톤처럼 관리합니다.
Spring Boot의 @Service, @Repository Bean 등록과 유사한 역할을 합니다.

공통 팩토리 함수를 제공하여 모든 Service에 재사용 가능합니다.
"""
from typing import Type, TypeVar, Callable
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.pos_neo.session import get_db_session

# Generic 타입 변수
T = TypeVar('T')


def get_service(service_class: Type[T]) -> Callable[[AsyncSession], T]:
    """
    Service Dependency 팩토리 함수 (공통)
    
    모든 Service에 공통으로 사용할 수 있는 Dependency 생성 함수입니다.
    Spring Boot의 @Service Bean 등록과 유사한 역할을 합니다.
    
    사용 예시:
        @router.get("/api/{api_id}")
        async def get_paths(
            api_id: str,
            service: GnRestUriPathService = Depends(get_service(GnRestUriPathService))
        ):
            return await service.get_paths_by_api_id(api_id)
    
    새로운 Service 추가 시:
        # Service 클래스만 정의하면 됨
        class UserService:
            def __init__(self, session: AsyncSession):
                self.session = session
        
        # Controller에서 바로 사용
        service: UserService = Depends(get_service(UserService))
    
    Args:
        service_class: Service 클래스 타입
        
    Returns:
        Callable: Dependency 함수 (FastAPI Depends에 사용 가능)
    """
    def _get_service(session: AsyncSession = Depends(get_db_session)) -> T:
        """
        실제 Service 인스턴스를 생성하는 내부 함수
        
        Args:
            session: SQLAlchemy 비동기 세션 (자동 주입)
            
        Returns:
            T: Service 인스턴스
        """
        return service_class(session)
    
    return _get_service

