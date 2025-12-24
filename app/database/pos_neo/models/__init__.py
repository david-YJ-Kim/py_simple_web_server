"""
Entity 모델 패키지

모든 Entity 모델을 여기서 import하여 사용합니다.
주의: ForeignKey 관계가 있는 모델은 참조되는 모델(GnRestUriDef)을 먼저 import해야 합니다.
"""
from app.database.pos_neo.models.base import Base, TimestampMixin, AuditMixin

# ForeignKey 관계: GnRestUriPath -> GnRestUriDef
# 따라서 GnRestUriDef를 먼저 import해야 ForeignKey가 정상 작동합니다.
from app.database.pos_neo.models.gn_rest_uri_def_model import GnRestUriDef
from app.database.pos_neo.models.gn_rest_uri_path_model import GnRestUriPath

__all__ = [
    "Base",
    "TimestampMixin",
    "AuditMixin",
    "GnRestUriDef",
    "GnRestUriPath",
]


