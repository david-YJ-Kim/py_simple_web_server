"""
Service 패키지

모든 비즈니스 서비스를 여기서 import하여 사용합니다.
"""
from app.service.gn_rest_uri_path_service import GnRestUriPathService
from app.service.dependencies import get_service

__all__ = [
    "GnRestUriPathService",
    "get_service",
]

