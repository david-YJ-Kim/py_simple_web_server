"""
HTTP Method Enum

Python에서만 사용하는 Enum으로, DB에는 VARCHAR로 저장됩니다.
"""
from enum import Enum


class HttpMethod(str, Enum):
    """
    HTTP Method Enum
    
    Spring Boot의 enum과 유사한 역할을 합니다.
    
    사용 예시:
        method_nm = HttpMethod.GET
        print(method_nm.value)  # "GET"
    """
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    
    def __str__(self) -> str:
        """문자열 표현"""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> "HttpMethod":
        """
        문자열로부터 HttpMethod Enum 생성
        
        Args:
            value: "GET", "POST", "PUT", "DELETE", "PATCH" 중 하나
            
        Returns:
            HttpMethod: 해당하는 Enum 값
            
        Raises:
            ValueError: 유효하지 않은 값인 경우
        """
        for method in cls:
            if method.value == value.upper():
                return method
        raise ValueError(f"Invalid HttpMethod value: {value}. Must be one of: GET, POST, PUT, DELETE, PATCH")

