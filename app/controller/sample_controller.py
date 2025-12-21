from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/simple", tags=["Simple"])

class BasicPayloadIvo(BaseModel):
    """ Post 요청 IVO 모델 """
    name: str = Field(..., description="메시지 기본 전문")

@router.get("/")
async def handle_get():
    print("handle get method")
    return {
        "status": 200,
        "message": "hello world"
    }

@router.post("/")
async def handle_post(payload: BasicPayloadIvo):
    print(f"handle post method, payload: {payload}")
    return {
        "status": 200,
        "message": "hello world",
        "recv_data": payload.dict()
    }


if __name__ == '__main__':
    print("sample controller has been created.")

# router export
sample_router = router