"""
사용 상태 Enum

Python에서만 사용하는 Enum으로, DB에는 VARCHAR로 저장됩니다.
"""
from enum import Enum


class UseStatus(str, Enum):
    """
    사용 상태 Enum
    
    Spring Boot의 enum과 유사한 역할을 합니다.
    
    사용 예시:
        use_stat_cd = UseStatus.USABLE
        print(use_stat_cd.value)  # "USABLE"
    """
    USABLE = "USABLE"      # 사용 가능
    UNUSABLE = "UNUSABLE"  # 사용 불가
    
    def __str__(self) -> str:
        """문자열 표현"""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> "UseStatus":
        """
        문자열로부터 UseStatus Enum 생성
        
        Args:
            value: "USABLE" 또는 "UNUSABLE" 문자열
            
        Returns:
            UseStatus: 해당하는 Enum 값
            
        Raises:
            ValueError: 유효하지 않은 값인 경우
        """
        for status in cls:
            if status.value == value.upper():
                return status
        raise ValueError(f"Invalid UseStatus value: {value}")

