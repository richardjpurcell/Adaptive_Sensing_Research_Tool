from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def ping():
    return {"status": "ok", "service": "awsrt", "version": "0.1.0"}
