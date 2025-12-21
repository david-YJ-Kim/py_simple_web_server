"""
SQLAlchemy Base 클래스 및 공통 Mixin

Spring Boot의 @MappedSuperclass와 유사한 역할
"""
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, String, func
from typing import Optional
from datetime import datetime


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 Base 클래스
    모든 Entity가 이 클래스를 상속받습니다.
    """
    pass

class ObjIdMixin:
    obj_id: Optional[str] = Column(
        "obj_id",
        String(100),
        primary_key=True,
        nullable= False,
        comment="레코드 ID"
    )



class TimestampMixin:
    """
    생성일시, 수정일시 Mixin 클래스
    Spring Boot의 @CreatedDate, @LastModifiedDate와 유사
    
    사용 예시:
        class User(Base, TimestampMixin):
            ...
    """
    crt_dt: datetime = Column(
        DateTime,
        default=func.current_timestamp(),
        nullable=True,
        comment="생성일시"
    )
    mdfy_dt: datetime = Column(
        DateTime,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=True,
        comment="수정일시"
    )


class AuditMixin:
    """
    감사(Audit) 정보 Mixin 클래스
    생성자, 수정자 정보를 포함합니다.
    
    사용 예시:
        class User(Base, AuditMixin):
            ...
    """
    crt_user_id: Optional[str] = Column(
        "crt_user_id",
        String(40),
        nullable=True,
        comment="생성자 ID"
    )
    mdfy_user_id: Optional[str] = Column(
        "mdfy_user_id",
        String(40),
        nullable=True,
        comment="수정자 ID"
    )

    tid: Optional[str] = Column(
        "tid",
        String(100),
        nullable=True,
        comment="트랜잭션 ID"
    )

class UseMixin:
    use_stat_cd: Optional[str] = Column(
        "use_stat_cd",
        String(40),
        nullable=True,
        comment="사용 상태 코드"
    )

class RecordNoteMixin:
    rsn_cd: Optional[str] = Column(
        "rsn_cd",
        String(100),
        nullable=True,
        comment="사유 코드"
    )

    trns_cm: Optional[str] = Column(
        "trns_cm",
        String(100),
        nullable=True,
        comment="변환 코드"
    )

