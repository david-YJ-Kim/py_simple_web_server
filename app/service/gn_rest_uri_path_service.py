"""
GnRestUriPath 비즈니스 서비스

GnRestUriPath 관련 비즈니스 로직을 처리하는 서비스 레이어
"""
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.database.pos_neo.repository import GnRestUriPathRepository
from app.database.pos_neo.models.gn_rest_uri_path_model import GnRestUriPath
from app.database.constant.use_stat_enum import UseStatus

# 로거 설정
logger = logging.getLogger(__name__)


class GnRestUriPathService:
    """
    GnRestUriPath 비즈니스 서비스 클래스
    
    Spring Boot의 @Service와 유사한 역할을 합니다.
    Controller에서 이 서비스를 호출하여 비즈니스 로직을 처리합니다.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Service 초기화
        
        Args:
            session: SQLAlchemy 비동기 세션
        """
        self.session = session
        self.repository = GnRestUriPathRepository(session)
    
    async def get_paths_by_api_id(self, api_id: str) -> List[GnRestUriPath]:
        """
        API ID로 경로 목록 조회 (비즈니스 로직)
        
        Args:
            api_id: API ID
            
        Returns:
            List[GnRestUriPath]: 경로 목록
        """
        logger.info(f"[GnRestUriPathService] get_paths_by_api_id 호출 - api_id: {api_id}")
        
        try:
            # Repository에서 데이터 조회
            paths = await self.repository.find_by_api_id(api_id)
            
            logger.info(f"[GnRestUriPathService] find_by_api_id 결과 - 조회된 경로 개수: {len(paths)}")
            
            # 조회된 경로 정보 로그 출력
            for idx, path in enumerate(paths, 1):
                logger.info(
                    f"[GnRestUriPathService] 경로 {idx}: "
                    f"obj_id={path.obj_id}, "
                    f"api_id={path.api_id}, "
                    f"path_order={path.path_order}, "
                    f"path_value={path.path_value}, "
                    f"use_stat_cd={path.use_stat_cd}"
                )
            
            return paths
            
        except Exception as e:
            logger.error(f"[GnRestUriPathService] get_paths_by_api_id 오류 발생 - api_id: {api_id}, error: {str(e)}")
            raise
    
    async def get_path_by_id(self, obj_id: str) -> GnRestUriPath:
        """
        ID로 단일 경로 조회 (비즈니스 로직)
        
        Args:
            obj_id: 경로 ID
            
        Returns:
            GnRestUriPath: 경로 엔티티
            
        Raises:
            HTTPException: 경로를 찾을 수 없는 경우
        """
        logger.info(f"[GnRestUriPathService] get_path_by_id 호출 - obj_id: {obj_id}")
        
        try:
            # Repository에서 데이터 조회
            path = await self.repository.find_by_id(obj_id)
            
            if not path:
                logger.warning(f"[GnRestUriPathService] 경로를 찾을 수 없음 - obj_id: {obj_id}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Path with id {obj_id} not found"
                )
            
            logger.info(
                f"[GnRestUriPathService] 경로 조회 성공 - "
                f"obj_id={path.obj_id}, "
                f"api_id={path.api_id}, "
                f"path_value={path.path_value}"
            )
            
            return path
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[GnRestUriPathService] get_path_by_id 오류 발생 - obj_id: {obj_id}, error: {str(e)}")
            raise
    
    async def create_path(
        self,
        api_id: str,
        path_order: int,
        path_value: str,
        is_param_use: bool = False,
        param_nm: Optional[str] = None,
        param_typ: Optional[str] = None,
        param_desc: Optional[str] = None,
        example_val: Optional[str] = None,
        use_stat_cd: Optional[UseStatus] = None,
        crt_user_id: Optional[str] = None,
        mdfy_user_id: Optional[str] = None,
        tid: Optional[str] = None,
        rsn_cd: Optional[str] = None,
        trns_cm: Optional[str] = None
    ) -> GnRestUriPath:
        """
        새로운 경로 생성 (INSERT)
        
        Spring Boot 예시:
            @PostMapping("/paths")
            public Path createPath(@RequestBody PathCreateRequest request) {
                return service.createPath(request);
            }
        
        Args:
            api_id: API ID (필수)
            path_order: 경로 순서 (필수)
            path_value: 경로 값 (필수)
            is_param_use: 파라미터 사용 여부 (기본값: False)
            param_nm: 파라미터 명 (선택)
            param_typ: 파라미터 타입 (선택)
            param_desc: 파라미터 설명 (선택)
            example_val: 예시 값 (선택)
            use_stat_cd: 사용 상태 코드 (선택, 기본값: USABLE)
            crt_user_id: 생성자 ID (선택)
            mdfy_user_id: 수정자 ID (선택)
            tid: 트랜잭션 ID (선택)
            rsn_cd: 사유 코드 (선택)
            trns_cm: 변환 코드 (선택)
            
        Returns:
            GnRestUriPath: 생성된 경로 엔티티
            
        Raises:
            HTTPException: 
                - 400: 중복된 (api_id, path_order) 조합
                - 409: 데이터베이스 제약 조건 위반
        """
        logger.info(
            f"[GnRestUriPathService] create_path 호출 - "
            f"api_id: {api_id}, path_order: {path_order}, path_value: {path_value}"
        )
        
        try:
            # 중복 체크: (api_id, path_order) 조합이 이미 존재하는지 확인
            existing_path = await self.repository.find_by_api_id_and_path_order(api_id, path_order)
            if existing_path:
                logger.warning(
                    f"[GnRestUriPathService] 중복된 경로 - "
                    f"api_id: {api_id}, path_order: {path_order}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Path with api_id '{api_id}' and path_order '{path_order}' already exists"
                )
            
            # 새 엔티티 생성
            # obj_id는 ObjIdMixin에서 자동 생성됨
            new_path = GnRestUriPath(
                api_id=api_id,
                path_order=path_order,
                path_value=path_value,
                is_param_use=is_param_use,
                param_nm=param_nm,
                param_typ=param_typ,
                param_desc=param_desc,
                example_val=example_val,
                use_stat_cd=use_stat_cd or UseStatus.USABLE,  # 기본값: USABLE
                crt_user_id=crt_user_id,
                mdfy_user_id=mdfy_user_id,
                tid=tid,
                rsn_cd=rsn_cd,
                trns_cm=trns_cm
            )
            
            # Repository를 통해 저장
            saved_path = await self.repository.save(new_path)
            
            logger.info(
                f"[GnRestUriPathService] 경로 생성 성공 - "
                f"obj_id: {saved_path.obj_id}, "
                f"api_id: {saved_path.api_id}, "
                f"path_order: {saved_path.path_order}, "
                f"path_value: {saved_path.path_value}"
            )
            
            return saved_path
            
        except HTTPException:
            raise
        except IntegrityError as e:
            logger.error(
                f"[GnRestUriPathService] 데이터베이스 제약 조건 위반 - "
                f"api_id: {api_id}, path_order: {path_order}, error: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Database constraint violation: {str(e.orig) if hasattr(e, 'orig') else str(e)}"
            )
        except Exception as e:
            logger.error(
                f"[GnRestUriPathService] create_path 오류 발생 - "
                f"api_id: {api_id}, path_order: {path_order}, error: {str(e)}"
            )
            raise

