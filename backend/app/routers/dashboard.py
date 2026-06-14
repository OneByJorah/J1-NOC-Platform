from fastapi import APIRouter, Depends

from .auth import get_current_user

router = APIRouter()


@router.get("/dashboard/overview")
def dashboard_overview(user=Depends(get_current_user)):
    return {"clients_online": 0, "alerts": 0, "score": 100}
