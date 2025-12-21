"""
GN_REST_URI_PATH Entity 모델

REST API URI 경로 정보를 관리하는 테이블
"""
from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, 
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime
from app.database.pos_neo.constants import TableNames

from app.database.pos_neo.models.base import Base, TimestampMixin, ObjIdMixin, AuditMixin, RecordNoteMixin, UseMixin


class GnRestUriPath(Base, ObjIdMixin, TimestampMixin, AuditMixin, RecordNoteMixin, UseMixin):
    __tablename__ = TableNames.GN_REST_URI_PATH
    __table_args__ = (
        # Unique Constraint: (api_id, path_order)
        UniqueConstraint('api_id', 'path_order', name='uk_gn_rest_uri_path_01'),
        # 인덱스 (필요시 추가)
        # Index('idx_api_id', 'api_id'),
        # Index('idx_path_order', 'path_order'),
        {'schema': 'public', 'comment': 'REST API URI 경로 정보'}
    )
    
    # Foreign Key: api_id -> gn_rest_uri_def(api_id)
    api_id: str = Column(
        "api_id",
        String(100),
        ForeignKey("gn_rest_uri_def.api_id", ondelete="CASCADE"),
        nullable=False,
        comment="API ID"
    )
    
    # 경로 순서
    path_order: int = Column(
        "path_order",
        Integer,
        nullable=False,
        comment="경로 순서"
    )
    
    # 경로 값
    path_value: str = Column(
        "path_value",
        String(100),
        nullable=False,
        comment="경로 값"
    )
    
    # 파라미터 사용 여부
    is_param_use: bool = Column(
        "is_param_use",
        Boolean,
        default=False,
        nullable=True,
        comment="파라미터 사용 여부"
    )
    
    # 파라미터 정보
    param_nm: Optional[str] = Column(
        "param_nm",
        String(100),
        nullable=True,
        comment="파라미터 명"
    )
    
    param_typ: Optional[str] = Column(
        "param_typ",
        String(40),
        nullable=True,
        comment="파라미터 타입"
    )
    
    param_desc: Optional[str] = Column(
        "param_desc",
        Text,
        nullable=True,
        comment="파라미터 설명"
    )
    
    example_val: Optional[str] = Column(
        "example_val",
        String(200),
        nullable=True,
        comment="예시 값"
    )
    



    # crt_dt, mdfy_dt는 TimestampMixin에서 상속
    
    # 관계 설정 (선택사항 - gn_rest_uri_def 테이블이 있을 경우)
    # gn_rest_uri_def = relationship(
    #     "GnRestUriDef",
    #     back_populates="uri_paths",
    #     foreign_keys=[api_id]
    # )
    
    def __repr__(self) -> str:
        """객체 문자열 표현 (디버깅용)"""
        return (
            f"<GnRestUriPath("
            f"obj_id='{self.obj_id}', "
            f"api_id='{self.api_id}', "
            f"path_order={self.path_order}, "
            f"path_value='{self.path_value}'"
            f")>"
        )

