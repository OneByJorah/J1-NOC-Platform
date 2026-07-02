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


class RoleUpdate(RoleBase):
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


class UserUpdate(UserBase):
    password: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None


class UserOut(UserBase):
    id: int
    is_active: bool
    is_locked: bool
    role: RoleOut

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: int
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


# ===================== TABS / NAVIGATION =====================


class TabBase(BaseModel):
    path: str
    label: str
    sort_order: Optional[int] = 0
    is_visible: Optional[bool] = True
    icon: Optional[str] = None


class TabCreate(TabBase):
    pass


class TabUpdate(BaseModel):
    path: Optional[str] = None
    label: Optional[str] = None
    sort_order: Optional[int] = None
    is_visible: Optional[bool] = None
    icon: Optional[str] = None


class TabOut(TabBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
