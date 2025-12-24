"""
GN_REST_URI_PATH Entity 모델

REST API URI 경로 정보를 관리하는 테이블
"""
from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, 
    ForeignKey, ForeignKeyConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.database.pos_neo.constants import TableNames

from app.database.pos_neo.models.base import Base, TimestampMixin, ObjIdMixin, AuditMixin, RecordNoteMixin, UseMixin

# ForeignKey 관계를 위해 GnRestUriDef를 실제로 import해야 함
# (TYPE_CHECKING이 아닌 실제 import)
from app.database.pos_neo.models.gn_rest_uri_def_model import GnRestUriDef


class GnRestUriPath(Base, ObjIdMixin, TimestampMixin, AuditMixin, RecordNoteMixin, UseMixin):
    """REST URI 경로 Entity"""
    # Base 클래스에서 __allow_unmapped__ 상속받음
    
    __tablename__ = TableNames.GN_REST_URI_PATH
    __table_args__ = (
        # Unique Constraint: (api_id, path_order)
        UniqueConstraint('api_id', 'path_order', name='uk_gn_rest_uri_path_01'),
        # 인덱스 (필요시 추가)
        # Index('idx_api_id', 'api_id'),
        # Index('idx_path_order', 'path_order'),
        {
            'schema': 'public',
            'comment': 'REST API URI 경로 정보',
            'quote': False  # 따옴표 없이 사용 (PostgreSQL이 자동으로 소문자 변환)
        }
    )
    
    # Foreign Key: api_id -> gn_rest_uri_def(api_id)
    # api_id: str  # 타입 힌팅 제거 (SQLAlchemy 2.0 호환성)
    # 모델 클래스를 직접 참조하여 ForeignKey 설정
    api_id = Column(
        "api_id",
        String(100),
        ForeignKey(GnRestUriDef.api_id, ondelete="CASCADE"),
        nullable=False,
        comment="API ID (Foreign Key to gn_rest_uri_def.api_id)"
    )
    
    # 경로 순서
    # path_order: int  # 타입 힌팅 제거
    path_order = Column(
        "path_order",
        Integer,
        nullable=False,
        comment="경로 순서"
    )
    
    # 경로 값
    # path_value: str  # 타입 힌팅 제거
    path_value = Column(
        "path_value",
        String(100),
        nullable=False,
        comment="경로 값"
    )
    
    # 파라미터 사용 여부
    # is_param_use: bool  # 타입 힌팅 제거
    is_param_use = Column(
        "is_param_use",
        Boolean,
        default=False,
        nullable=True,
        comment="파라미터 사용 여부"
    )
    
    # 파라미터 정보
    # param_nm: Optional[str]  # 타입 힌팅 제거
    param_nm = Column(
        "param_nm",
        String(100),
        nullable=True,
        comment="파라미터 명"
    )
    
    # param_typ: Optional[str]  # 타입 힌팅 제거
    param_typ = Column(
        "param_typ",
        String(40),
        nullable=True,
        comment="파라미터 타입"
    )
    
    # param_desc: Optional[str]  # 타입 힌팅 제거
    param_desc = Column(
        "param_desc",
        Text,
        nullable=True,
        comment="파라미터 설명"
    )
    
    # example_val: Optional[str]  # 타입 힌팅 제거
    example_val = Column(
        "example_val",
        String(200),
        nullable=True,
        comment="예시 값"
    )
    



    # crt_dt, mdfy_dt는 TimestampMixin에서 상속
    
    # 관계 설정: gn_rest_uri_def와의 N:1 관계 (ManyToOne)
    # ForeignKeyConstraint를 사용하므로 relationship에서 ForeignKey를 찾지 않도록 설정
    gn_rest_uri_def = relationship(
        "GnRestUriDef",
        back_populates="uri_paths",
        primaryjoin="GnRestUriPath.api_id == GnRestUriDef.api_id",
        foreign_keys=[api_id]
    )
    
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


