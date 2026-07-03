from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from ..database import SessionLocal
from ..models import User, Role
from .auth import get_password_hash

router = APIRouter()


class OnboardingStatusResponse(BaseModel):
    needs_setup: bool


class OnboardingCreateRequest(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str
    full_name: str | None = None


class OnboardingCreateResponse(BaseModel):
    message: str
    username: str


@router.get("/setup/status", response_model=OnboardingStatusResponse)
def setup_status():
    db = SessionLocal()
    try:
        user_count = db.query(User).filter(User.is_active == True).count()
        return OnboardingStatusResponse(needs_setup=user_count == 0)
    finally:
        db.close()


@router.post("/setup", response_model=OnboardingCreateResponse, status_code=status.HTTP_201_CREATED)
def create_first_admin(payload: OnboardingCreateRequest):
    db = SessionLocal()
    try:
        # Guard: only allow setup when no active users exist
        user_count = db.query(User).filter(User.is_active == True).count()
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Setup already completed. Contact an existing admin.",
            )

        # Ensure an admin role exists
        admin_role = db.query(Role).filter(Role.slug == "admin").first()
        if not admin_role:
            admin_role = Role(
                name="Administrator",
                slug="admin",
                description="Full platform access",
                permissions={"*": True},
                is_system=True,
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        if db.query(User).filter(User.username == payload.username).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

        user = User(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            role_id=admin_role.id,
            hashed_password=get_password_hash(payload.password),
            is_active=True,
        )
        db.add(user)
        db.commit()

        return OnboardingCreateResponse(message="Admin account created. You can now log in.", username=user.username)
    finally:
        db.close()
