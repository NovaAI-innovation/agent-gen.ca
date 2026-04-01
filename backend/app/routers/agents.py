from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_agents():
    return {"message": "Agents API"}

@router.post("/")
def create_agent():
    return {"message": "Create agent"}
