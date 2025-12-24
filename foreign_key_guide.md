# SQLAlchemy Foreign Key 가이드

## 1. Foreign Key란?

**Foreign Key (외래키)**는 한 테이블의 컬럼이 다른 테이블의 Primary Key나 Unique Key를 참조하는 제약조건입니다.

### 역할
- **참조 무결성 보장**: 참조하는 테이블에 데이터가 존재해야만 INSERT 가능
- **관계 설정**: 두 테이블 간의 관계를 명시적으로 정의
- **CASCADE 옵션**: 부모 데이터 삭제 시 자식 데이터도 함께 삭제 (ondelete="CASCADE")

### 예시
```sql
-- gn_rest_uri_path 테이블의 api_id가
-- gn_rest_uri_def 테이블의 api_id를 참조
gn_rest_uri_path.api_id → gn_rest_uri_def.api_id
```

---

## 2. SQLAlchemy에서 Foreign Key 정의 방법

### 방법 1: Column 레벨 ForeignKey (권장)

```python
from sqlalchemy import Column, String, ForeignKey
from app.database.pos_neo.models.gn_rest_uri_def_model import GnRestUriDef

class GnRestUriPath(Base):
    api_id = Column(
        "api_id",
        String(100),
        ForeignKey(GnRestUriDef.api_id, ondelete="CASCADE"),  # 모델 클래스 직접 참조
        nullable=False
    )
```

**장점:**
- 간단하고 직관적
- SQLAlchemy가 자동으로 관계를 인식
- relationship과 함께 사용하기 쉬움

**주의사항:**
- 참조하는 모델 클래스를 **실제로 import**해야 함
- `TYPE_CHECKING`으로는 안됨 (런타임에 import 필요)

---

### 방법 2: 테이블 레벨 ForeignKeyConstraint

```python
from sqlalchemy import ForeignKeyConstraint

class GnRestUriPath(Base):
    __table_args__ = (
        ForeignKeyConstraint(
            ['api_id'],                    # 현재 테이블의 컬럼
            ['gn_rest_uri_def.api_id'],    # 참조하는 테이블.컬럼 (문자열)
            ondelete='CASCADE',
            name='fk_gn_rest_uri_path_api_id'
        ),
    )
    
    api_id = Column("api_id", String(100), nullable=False)
```

**장점:**
- 복합 Foreign Key 정의 가능
- 제약조건 이름을 명시적으로 지정 가능

**단점:**
- relationship이 ForeignKey를 자동으로 찾지 못할 수 있음
- `primaryjoin`을 명시적으로 지정해야 할 수 있음

---

## 3. 발생했던 문제들과 해결 방법

### 문제 1: ForeignKey가 테이블을 찾지 못함

**에러:**
```
NoReferencedTableError: Foreign key associated with column 'gn_rest_uri_path.api_id' 
could not find table 'gn_rest_uri_def'
```

**원인:**
- `TYPE_CHECKING`으로 import하면 런타임에 import되지 않음
- ForeignKey에서 문자열로 테이블 이름을 지정했지만 SQLAlchemy가 찾지 못함

**해결:**
```python
# ❌ 잘못된 방법
if TYPE_CHECKING:
    from app.database.pos_neo.models.gn_rest_uri_def_model import GnRestUriDef

# ✅ 올바른 방법
from app.database.pos_neo.models.gn_rest_uri_def_model import GnRestUriDef
```

---

### 문제 2: 테이블 이름 대소문자 불일치

**원인:**
- `quote: False`로 인해 PostgreSQL이 테이블 이름을 소문자로 변환
- 하지만 `__tablename__`이 대문자로 설정되어 있음

**해결:**
```python
# table_names.py
GN_REST_URI_DEF = "gn_rest_uri_def"  # 소문자로 통일

# 또는 ForeignKey에서 직접 소문자 사용
ForeignKey("gn_rest_uri_def.api_id", ...)
```

---

### 문제 3: relationship이 ForeignKey를 찾지 못함

**에러:**
```
NoForeignKeysError: Could not determine join condition between parent/child tables
```

**원인:**
- ForeignKeyConstraint를 사용하면 Column 레벨 ForeignKey가 없음
- relationship이 ForeignKey를 자동으로 찾지 못함

**해결:**
```python
# primaryjoin을 명시적으로 지정
gn_rest_uri_def = relationship(
    "GnRestUriDef",
    back_populates="uri_paths",
    primaryjoin="GnRestUriPath.api_id == GnRestUriDef.api_id",
    foreign_keys=[api_id]
)
```

---

## 4. 최종 권장 방법

### ✅ 권장: Column 레벨 ForeignKey + 모델 클래스 직접 참조

```python
# gn_rest_uri_path_model.py
from app.database.pos_neo.models.gn_rest_uri_def_model import GnRestUriDef

class GnRestUriPath(Base):
    __tablename__ = "gn_rest_uri_path"
    
    api_id = Column(
        "api_id",
        String(100),
        ForeignKey(GnRestUriDef.api_id, ondelete="CASCADE"),  # 모델 클래스 직접 참조
        nullable=False
    )
    
    # relationship은 ForeignKey를 자동으로 찾음
    gn_rest_uri_def = relationship(
        "GnRestUriDef",
        back_populates="uri_paths"
    )
```

**장점:**
- 가장 간단하고 직관적
- SQLAlchemy가 자동으로 관계를 인식
- relationship 설정이 간단함

---

## 5. 관계 설정 (relationship)

### OneToMany (1:N) 관계

```python
# gn_rest_uri_def_model.py (부모)
class GnRestUriDef(Base):
    api_id = Column("api_id", String(100), primary_key=True)
    
    # 1:N 관계: 하나의 정의에 여러 경로
    uri_paths = relationship(
        "GnRestUriPath",
        back_populates="gn_rest_uri_def",
        cascade="all, delete-orphan"  # 부모 삭제 시 자식도 삭제
    )
```

### ManyToOne (N:1) 관계

```python
# gn_rest_uri_path_model.py (자식)
class GnRestUriPath(Base):
    api_id = Column(
        "api_id",
        String(100),
        ForeignKey(GnRestUriDef.api_id, ondelete="CASCADE"),
        nullable=False
    )
    
    # N:1 관계: 여러 경로가 하나의 정의를 참조
    gn_rest_uri_def = relationship(
        "GnRestUriDef",
        back_populates="uri_paths"
    )
```

---

## 6. 주의사항

### 1. 모델 import 순서

```python
# ✅ 올바른 순서
from app.database.pos_neo.models.gn_rest_uri_def_model import GnRestUriDef  # 먼저
from app.database.pos_neo.models.gn_rest_uri_path_model import GnRestUriPath  # 나중

# 또는 __init__.py에서 순서 보장
from app.database.pos_neo.models.gn_rest_uri_def_model import GnRestUriDef
from app.database.pos_neo.models.gn_rest_uri_path_model import GnRestUriPath
```

### 2. 순환 참조 방지

```python
# ✅ 올바른 방법: relationship에서 문자열 사용
uri_paths = relationship("GnRestUriPath", ...)  # 문자열로 참조

# ❌ 잘못된 방법: 직접 import하면 순환 참조 발생 가능
from app.database.pos_neo.models.gn_rest_uri_path_model import GnRestUriPath
uri_paths = relationship(GnRestUriPath, ...)  # 직접 참조 (순환 참조 위험)
```

### 3. 테이블 이름 일치

```python
# __tablename__과 ForeignKey의 테이블 이름이 일치해야 함
__tablename__ = "gn_rest_uri_def"  # 소문자
ForeignKey("gn_rest_uri_def.api_id", ...)  # 소문자로 일치
```

### 4. quote: False 사용 시

```python
__table_args__ = {
    'quote': False  # PostgreSQL이 자동으로 소문자 변환
}

# 따라서 __tablename__도 소문자로 설정
__tablename__ = "gn_rest_uri_def"  # 소문자
```

---

## 7. 현재 프로젝트의 최종 구조

### gn_rest_uri_def_model.py
```python
class GnRestUriDef(Base):
    __tablename__ = "gn_rest_uri_def"
    
    api_id = Column("api_id", String(100), unique=True, nullable=False)
    
    # 1:N 관계
    uri_paths = relationship(
        "GnRestUriPath",
        back_populates="gn_rest_uri_def",
        cascade="all, delete-orphan"
    )
```

### gn_rest_uri_path_model.py
```python
from app.database.pos_neo.models.gn_rest_uri_def_model import GnRestUriDef

class GnRestUriPath(Base):
    __tablename__ = "gn_rest_uri_path"
    
    # ForeignKey: 모델 클래스 직접 참조
    api_id = Column(
        "api_id",
        String(100),
        ForeignKey(GnRestUriDef.api_id, ondelete="CASCADE"),
        nullable=False
    )
    
    # N:1 관계
    gn_rest_uri_def = relationship(
        "GnRestUriDef",
        back_populates="uri_paths"
    )
```

---

## 8. 요약

1. **ForeignKey는 Column 레벨에서 모델 클래스를 직접 참조하는 것이 가장 간단**
2. **참조하는 모델을 실제로 import해야 함** (TYPE_CHECKING 아님)
3. **테이블 이름은 소문자로 통일** (quote: False 사용 시)
4. **relationship은 ForeignKey를 자동으로 찾음** (명시적 설정 불필요)
5. **모델 import 순서를 보장** (참조되는 모델을 먼저 import)

