"""
GnRestUriPath Controller

REST API URI 경로 관련 API 엔드포인트를 제공합니다.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field

from app.service import GnRestUriPathService, get_service
from app.database.pos_neo.models.gn_rest_uri_path_model import GnRestUriPath
from app.database.constant.use_stat_enum import UseStatus

router = APIRouter(prefix="/api/v1/uri-paths", tags=["URI Paths"])


# Request Schema
class PathCreateRequest(BaseModel):
    """경로 생성 요청 스키마"""
    api_id: str = Field(..., description="API ID", min_length=1, max_length=100)
    path_order: int = Field(..., description="경로 순서", ge=0)
    path_value: str = Field(..., description="경로 값", min_length=1, max_length=100)
    is_param_use: bool = Field(default=False, description="파라미터 사용 여부")
    param_nm: Optional[str] = Field(default=None, description="파라미터 명", max_length=100)
    param_typ: Optional[str] = Field(default=None, description="파라미터 타입", max_length=40)
    param_desc: Optional[str] = Field(default=None, description="파라미터 설명")
    example_val: Optional[str] = Field(default=None, description="예시 값", max_length=200)
    use_stat_cd: Optional[str] = Field(default="USABLE", description="사용 상태 코드 (USABLE/UNUSABLE)")
    crt_user_id: Optional[str] = Field(default=None, description="생성자 ID", max_length=40)
    mdfy_user_id: Optional[str] = Field(default=None, description="수정자 ID", max_length=40)
    tid: Optional[str] = Field(default=None, description="트랜잭션 ID", max_length=100)
    rsn_cd: Optional[str] = Field(default=None, description="사유 코드", max_length=100)
    trns_cm: Optional[str] = Field(default=None, description="변환 코드", max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "api_id": "PATH001",
                "path_order": 1,
                "path_value": "users",
                "is_param_use": False,
                "use_stat_cd": "USABLE"
            }
        }


# Response Schema
class PathResponse(BaseModel):
    """경로 응답 스키마"""
    obj_id: str
    api_id: str
    path_order: int
    path_value: str
    use_stat_cd: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/api/{api_id}", response_model=List[PathResponse])
async def get_paths_by_api_id(
    api_id: str,
    service: GnRestUriPathService = Depends(get_service(GnRestUriPathService))  # ← 공통 팩토리 사용
):
    print("request received.")
    """
    API ID로 경로 목록 조회
    
    Spring Boot 예시:
        @GetMapping("/api/{apiId}")
        public List<Path> getPaths(
            @PathVariable String apiId,
            @Autowired GnRestUriPathService service
        ) {
            return service.getPathsByApiId(apiId);
        }
    
    Args:
        api_id: API ID
        service: GnRestUriPathService (자동 주입)
        
    Returns:
        List[PathResponse]: 경로 목록
    """
    paths = await service.get_paths_by_api_id(api_id)
    return paths


@router.get("/{obj_id}", response_model=PathResponse)
async def get_path_by_id(
    obj_id: str,
    service: GnRestUriPathService = Depends(get_service(GnRestUriPathService))  # ← 공통 팩토리 사용
):
    """
    ID로 단일 경로 조회
    
    Args:
        obj_id: 경로 ID
        service: GnRestUriPathService (자동 주입)
        
    Returns:
        PathResponse: 경로 정보
    """
    path = await service.get_path_by_id(obj_id)
    return path


@router.post("", response_model=PathResponse, status_code=status.HTTP_201_CREATED)
async def create_path(
    request: PathCreateRequest,
    service: GnRestUriPathService = Depends(get_service(GnRestUriPathService))  # ← 공통 팩토리 사용
):
    """
    새로운 경로 생성 (INSERT)
    
    Spring Boot 예시:
        @PostMapping("/paths")
        public ResponseEntity<Path> createPath(@RequestBody PathCreateRequest request) {
            Path path = service.createPath(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(path);
        }
    
    Args:
        request: 경로 생성 요청 데이터
        service: GnRestUriPathService (자동 주입)
        
    Returns:
        PathResponse: 생성된 경로 정보 (HTTP 201 Created)
    """
    # use_stat_cd 문자열을 UseStatus Enum으로 변환
    use_status = None
    if request.use_stat_cd:
        try:
            use_status = UseStatus.from_string(request.use_stat_cd)
        except ValueError:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid use_stat_cd: {request.use_stat_cd}. Must be 'USABLE' or 'UNUSABLE'"
            )
    
    # Service 호출
    path = await service.create_path(
        api_id=request.api_id,
        path_order=request.path_order,
        path_value=request.path_value,
        is_param_use=request.is_param_use,
        param_nm=request.param_nm,
        param_typ=request.param_typ,
        param_desc=request.param_desc,
        example_val=request.example_val,
        use_stat_cd=use_status,
        crt_user_id=request.crt_user_id,
        mdfy_user_id=request.mdfy_user_id,
        tid=request.tid,
        rsn_cd=request.rsn_cd,
        trns_cm=request.trns_cm
    )
    
    return path


# router export
gn_rest_uri_path_router = router

