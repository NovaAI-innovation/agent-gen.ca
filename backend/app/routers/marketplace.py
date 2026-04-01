from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def marketplace():
    return {"message": "Agent Marketplace"}
