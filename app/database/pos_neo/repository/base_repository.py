"""
Base Repository 클래스

Spring Boot의 JpaRepository<T, ID>와 유사한 역할을 합니다.
모든 Repository가 이 클래스를 상속받아 기본 CRUD 메서드를 사용할 수 있습니다.
"""
from typing import Generic, TypeVar, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

# Generic 타입 변수
T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base Repository 클래스
    
    Spring Boot JPA 예시:
        public interface UserRepository extends JpaRepository<User, Long> {
            Optional<User> findById(Long id);
            List<User> findAll();
            User save(User user);
            void delete(User user);
        }
    
    사용 예시:
        class UserRepository(BaseRepository[User]):
            def __init__(self, session: AsyncSession):
                super().__init__(session, User)
    """
    
    def __init__(self, session: AsyncSession, model: type[T]):
        """
        Repository 초기화
        
        Args:
            session: SQLAlchemy 비동기 세션
            model: Entity 모델 클래스
        """
        self.session = session
        self.model = model
    
    async def find_by_id(self, obj_id: str) -> Optional[T]:
        """
        ID로 단일 엔티티 조회
        
        Spring Boot: Optional<T> findById(ID id)
        
        Args:
            obj_id: Primary Key 값
            
        Returns:
            Optional[T]: 조회된 엔티티, 없으면 None
        """
        result = await self.session.execute(
            select(self.model).where(self.model.obj_id == obj_id)
        )
        return result.scalar_one_or_none()
    
    async def find_all(self) -> List[T]:
        """
        전체 엔티티 조회
        
        Spring Boot: List<T> findAll()
        
        Returns:
            List[T]: 전체 엔티티 리스트
        """
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())
    
    async def save(self, entity: T) -> T:
        """
        엔티티 저장 (INSERT or UPDATE)
        
        Spring Boot: <S extends T> S save(S entity)
        
        Args:
            entity: 저장할 엔티티
            
        Returns:
            T: 저장된 엔티티 (ID 등이 채워진 상태)
        """
        self.session.add(entity)
        await self.session.flush()  # DB에 반영 (트랜잭션은 아직 커밋 안됨)
        await self.session.refresh(entity)  # DB에서 최신 데이터 가져오기
        return entity
    
    async def save_all(self, entities: List[T]) -> List[T]:
        """
        여러 엔티티 일괄 저장
        
        Spring Boot: <S extends T> List<S> saveAll(Iterable<S> entities)
        
        Args:
            entities: 저장할 엔티티 리스트
            
        Returns:
            List[T]: 저장된 엔티티 리스트
        """
        self.session.add_all(entities)
        await self.session.flush()
        for entity in entities:
            await self.session.refresh(entity)
        return entities
    
    async def delete(self, entity: T) -> None:
        """
        엔티티 삭제
        
        Spring Boot: void delete(T entity)
        
        Args:
            entity: 삭제할 엔티티
        """
        await self.session.delete(entity)
        await self.session.flush()
    
    async def delete_by_id(self, obj_id: str) -> bool:
        """
        ID로 엔티티 삭제
        
        Spring Boot: void deleteById(ID id)
        
        Args:
            obj_id: 삭제할 엔티티의 Primary Key
            
        Returns:
            bool: 삭제 성공 여부 (엔티티가 존재했으면 True)
        """
        entity = await self.find_by_id(obj_id)
        if entity:
            await self.delete(entity)
            return True
        return False
    
    async def exists_by_id(self, obj_id: str) -> bool:
        """
        ID로 엔티티 존재 여부 확인
        
        Spring Boot: boolean existsById(ID id)
        
        Args:
            obj_id: 확인할 Primary Key
            
        Returns:
            bool: 엔티티 존재 여부
        """
        entity = await self.find_by_id(obj_id)
        return entity is not None
    
    async def count(self) -> int:
        """
        전체 엔티티 개수 조회
        
        Spring Boot: long count()
        
        Returns:
            int: 전체 엔티티 개수
        """
        result = await self.session.execute(
            select(self.model).with_only_columns(self.model.obj_id)
        )
        return len(list(result.scalars().all()))

