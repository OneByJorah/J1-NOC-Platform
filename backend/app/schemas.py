from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class RoleBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    permissions: dict = {}


class RoleCreate(RoleBase):
    pass


class RoleOut(RoleBase):
    id: int

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role_id: int


class UserOut(UserBase):
    id: int
    is_active: bool
    role: RoleOut

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: int
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
