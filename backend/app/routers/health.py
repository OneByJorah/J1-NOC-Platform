from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", include_in_schema=False)
@router.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}
