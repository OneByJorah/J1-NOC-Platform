from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr

from ..config import get_settings
from ..database import SessionLocal
from ..models import User

router = APIRouter()

settings = get_settings()

import bcrypt

pwd_context = bcrypt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

ALGORITHM = "HS256"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None
    scopes: list[str] = []


class UserOut(BaseModel):
    id: int
    username: str | None
    email: EmailStr | None
    full_name: str | None
    role: str | None

    model_config = {"from_attributes": True}


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
        return user
    finally:
        db.close()


def require_roles(*roles: str):
    async def checker(current_user: User = Depends(get_current_user)):
        if current_user.role.slug not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return checker


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/login", response_model=Token)
async def login(payload: LoginRequest):
    username = str(payload.username)
    password = str(payload.password)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user is None or not verify_password(password, str(user.hashed_password) if user.hashed_password is not None else ""):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = create_access_token({"sub": user.username or username, "scopes": [user.role.name]})
        return Token(access_token=token, token_type="bearer")
    finally:
        db.close()
