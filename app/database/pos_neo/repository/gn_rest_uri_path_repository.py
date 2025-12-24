"""
GnRestUriPath Repository

GnRestUriPath Entity 전용 Repository
BaseRepository를 상속받아 기본 CRUD 메서드를 사용하고,
추가로 커스텀 쿼리 메서드를 구현합니다.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database.pos_neo.repository.base_repository import BaseRepository
from app.database.pos_neo.models.gn_rest_uri_path_model import GnRestUriPath
from app.database.constant.use_stat_enum import UseStatus


class GnRestUriPathRepository(BaseRepository[GnRestUriPath]):
    """
    GnRestUriPath 전용 Repository
    
    Spring Boot 예시:
        @Repository
        public interface GnRestUriPathRepository extends JpaRepository<GnRestUriPath, String> {
            List<GnRestUriPath> findByApiId(String apiId);
            List<GnRestUriPath> findByUseStatCd(UseStatus useStatCd);
        }
    
    사용 예시:
        async with get_db_session() as session:
            repo = GnRestUriPathRepository(session)
            paths = await repo.find_by_api_id("api_001")
    """
    
    def __init__(self, session: AsyncSession):
        """
        Repository 초기화
        
        Args:
            session: SQLAlchemy 비동기 세션
        """
        super().__init__(session, GnRestUriPath)
    
    async def find_by_api_id(self, api_id: str) -> List[GnRestUriPath]:
        """
        API ID로 경로 목록 조회 (경로 순서로 정렬)
        
        Args:
            api_id: API ID
            
        Returns:
            List[GnRestUriPath]: 해당 API의 경로 목록 (path_order 오름차순)
        """
        result = await self.session.execute(
            select(GnRestUriPath)
            .where(GnRestUriPath.api_id == api_id)
            .order_by(GnRestUriPath.path_order)
        )
        return list(result.scalars().all())
    
    async def find_by_api_id_and_path_order(
        self, 
        api_id: str, 
        path_order: int
    ) -> Optional[GnRestUriPath]:
        """
        API ID와 경로 순서로 단일 경로 조회
        
        Args:
            api_id: API ID
            path_order: 경로 순서
            
        Returns:
            Optional[GnRestUriPath]: 조회된 경로, 없으면 None
        """
        result = await self.session.execute(
            select(GnRestUriPath)
            .where(
                and_(
                    GnRestUriPath.api_id == api_id,
                    GnRestUriPath.path_order == path_order
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def find_by_use_status(
        self, 
        use_status: UseStatus
    ) -> List[GnRestUriPath]:
        """
        사용 상태로 경로 목록 조회
        
        Args:
            use_status: 사용 상태 (UseStatus.USABLE 또는 UseStatus.UNUSABLE)
            
        Returns:
            List[GnRestUriPath]: 해당 상태의 경로 목록
        """
        result = await self.session.execute(
            select(GnRestUriPath)
            .where(GnRestUriPath.use_stat_cd == use_status)
            .order_by(GnRestUriPath.api_id, GnRestUriPath.path_order)
        )
        return list(result.scalars().all())
    
    async def find_usable_paths(self) -> List[GnRestUriPath]:
        """
        사용 가능한 경로 목록 조회 (편의 메서드)
        
        Returns:
            List[GnRestUriPath]: 사용 가능한 경로 목록
        """
        return await self.find_by_use_status(UseStatus.USABLE)
    
    async def find_unusable_paths(self) -> List[GnRestUriPath]:
        """
        사용 불가능한 경로 목록 조회 (편의 메서드)
        
        Returns:
            List[GnRestUriPath]: 사용 불가능한 경로 목록
        """
        return await self.find_by_use_status(UseStatus.UNUSABLE)
    
    async def find_by_api_id_and_use_status(
        self,
        api_id: str,
        use_status: UseStatus
    ) -> List[GnRestUriPath]:
        """
        API ID와 사용 상태로 경로 목록 조회
        
        Args:
            api_id: API ID
            use_status: 사용 상태
            
        Returns:
            List[GnRestUriPath]: 해당 조건의 경로 목록
        """
        result = await self.session.execute(
            select(GnRestUriPath)
            .where(
                and_(
                    GnRestUriPath.api_id == api_id,
                    GnRestUriPath.use_stat_cd == use_status
                )
            )
            .order_by(GnRestUriPath.path_order)
        )
        return list(result.scalars().all())
    
    async def count_by_api_id(self, api_id: str) -> int:
        """
        API ID로 경로 개수 조회
        
        Args:
            api_id: API ID
            
        Returns:
            int: 해당 API의 경로 개수
        """
        result = await self.session.execute(
            select(GnRestUriPath)
            .where(GnRestUriPath.api_id == api_id)
            .with_only_columns(GnRestUriPath.obj_id)
        )
        return len(list(result.scalars().all()))


