# Simple Web Server w/ Python



## 📁 프로젝트 구조

```
root/
├── app/
│   ├── entity/
│   │   ├── ua_lcn_task_mng_note_pos_entity.py    # Note 엔티티
│   │   └── ua_lcn_task_mng_item_pos_entity.py    # 기존 Item 엔티티
│   ├── schemas/
│   │   ├── ua_lcn_task_mng_note_pos_schema.py    # Note 스키마
│   │   └── ua_lcn_task_mng_item_pos_schema.py    # 기존 Item 스키마
│   ├── services/
│   │   ├── note_service.py                        # Note 서비스
│   │   └── markdown_service.py                    # 기존 서비스
│   ├── controllers/
│   │   └── note_controller.py                     # Note 컨트롤러
│   ├── dependencies/
│   │   └── database.py                            # 데이터베이스 의존성
│   ├── constants/
│   │   ├── table_names_enum.py                    # 테이블 이름 열거형
│   │   └── yn_flag_enum.py                        # Y/N 플래그 열거형
│   ├── utils/
│   │   └── common_utils.py                        # 공통 유틸리티
│   └── main.py                                    # FastAPI 앱
├── tests/
│   └── test_note_schema.py                        # Note 스키마 테스트
└── docs/
    ├── DESIGN.md                                   # 시스템 설계 문서
    ├── API_DESIGN.md                               # API 설계 문서
    └── DEVELOPMENT_GUIDE.md                        # 개발 가이드
```
## DB 연결 구분 방식
멀티 데이터 소스를 지원하는 어플리케이션으로 DB별 호스팅별 설정을 구분함
구분 기준: DB 타입별 * 호스팅별
### DB 타입
- PostgreSQL : POS
- Oracle : OCR
- MySQL  : MSQ
- Sqlite : SQL

### 호스팅별
호스팅 사이트 약자로 구분함
- NeonDB : NEO
- ??????? : ABS
- 로컬 : LCL
### DB 구분
- POS_NEO: PostgreSQL + NeonDB
- SQL_LCL: Sqlite + Local



## 🛠️ 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 테이블 생성
```bash
python -m app.dependencies.database
```

### 3. 서버 실행
```bash
python -m app.main
```


### 3. 서버 실행 (Docker)
```bash
python -m app.main
```

### 4. 테스트 실행
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```