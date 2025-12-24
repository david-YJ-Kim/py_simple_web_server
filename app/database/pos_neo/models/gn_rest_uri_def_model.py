"""
GN_REST_URI_DEF Entity 모델

REST API URI 정의 정보를 관리하는 테이블
"""
from sqlalchemy import (
    Column, String, Text, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from typing import Optional
from app.database.pos_neo.constants import TableNames

from app.database.pos_neo.models.base import Base, TimestampMixin, ObjIdMixin, AuditMixin, RecordNoteMixin, UseMixin


class GnRestUriDef(Base, ObjIdMixin, TimestampMixin, AuditMixin, RecordNoteMixin, UseMixin):
    """REST URI 정의 Entity"""
    # Base 클래스에서 __allow_unmapped__ 상속받음
    
    __tablename__ = TableNames.GN_REST_URI_DEF
    __table_args__ = (
        # Unique Constraint: api_id
        UniqueConstraint('api_id', name='gn_rest_uri_def_api_id_key'),
        # Check Constraint: method_nm은 GET, POST, PUT, DELETE, PATCH 중 하나
        CheckConstraint(
            "method_nm IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')",
            name='gn_rest_uri_def_method_nm_check'
        ),
        {
            'schema': 'public',
            'comment': 'REST API URI 정의 정보',
            'quote': False  # 따옴표 없이 사용 (PostgreSQL이 자동으로 소문자 변환)
        }
    )
    
    # API ID (Unique)
    # api_id: str  # 타입 힌팅 제거 (SQLAlchemy 2.0 호환성)
    api_id = Column(
        "api_id",
        String(100),
        nullable=False,
        unique=True,  # UNIQUE 제약조건
        comment="API ID (Unique)"
    )
    
    # 사이트 ID
    # site_id: str  # 타입 힌팅 제거
    site_id = Column(
        "site_id",
        String(40),
        nullable=False,
        comment="사이트 ID"
    )
    
    # 서비스 명
    # srv_nm: str  # 타입 힌팅 제거
    srv_nm = Column(
        "srv_nm",
        String(40),
        nullable=False,
        comment="서비스 명"
    )
    
    # HTTP Method (GET, POST, PUT, DELETE, PATCH)
    # method_nm: Optional[str]  # 타입 힌팅 제거
    method_nm = Column(
        "method_nm",
        String(10),
        nullable=True,
        comment="HTTP Method (GET, POST, PUT, DELETE, PATCH)"
    )
    
    # API 명
    # api_nm: Optional[str]  # 타입 힌팅 제거
    api_nm = Column(
        "api_nm",
        String(40),
        nullable=True,
        comment="API 명"
    )
    
    # API 설명
    # api_desc: Optional[str]  # 타입 힌팅 제거
    api_desc = Column(
        "api_desc",
        Text,
        nullable=True,
        comment="API 설명"
    )
    
    # Base URI
    # base_uri: Optional[str]  # 타입 힌팅 제거
    base_uri = Column(
        "base_uri",
        String(100),
        nullable=True,
        comment="Base URI"
    )
    
    # Version 정보
    # version_inf: Optional[str]  # 타입 힌팅 제거
    version_inf = Column(
        "version_inf",
        String(20),
        nullable=True,
        comment="Version 정보"
    )
    
    # crt_dt, mdfy_dt는 TimestampMixin에서 상속
    # crt_user_id, mdfy_user_id, tid는 AuditMixin에서 상속
    # use_stat_cd는 UseMixin에서 상속
    # rsn_cd, trns_cm은 RecordNoteMixin에서 상속
    
    # 관계 설정: gn_rest_uri_path와의 1:N 관계 (OneToMany)
    # ForeignKeyConstraint를 사용하므로 relationship에서 ForeignKey를 찾지 않도록 설정
    uri_paths = relationship(
        "GnRestUriPath",
        back_populates="gn_rest_uri_def",
        primaryjoin="GnRestUriDef.api_id == GnRestUriPath.api_id",
        foreign_keys="[GnRestUriPath.api_id]",
        cascade="all, delete-orphan"  # 부모 삭제 시 자식도 삭제
    )
    
    def __repr__(self) -> str:
        """객체 문자열 표현 (디버깅용)"""
        return (
            f"<GnRestUriDef("
            f"obj_id='{self.obj_id}', "
            f"api_id='{self.api_id}', "
            f"site_id='{self.site_id}', "
            f"srv_nm='{self.srv_nm}', "
            f"method_nm='{self.method_nm}'"
            f")>"
        )

