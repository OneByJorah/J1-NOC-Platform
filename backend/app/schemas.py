from datetime import datetime

from pydantic import BaseModel, EmailStr


class RoleBase(BaseModel):
    name: str
    slug: str
    description: str | None = None
    permissions: dict = {}


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleOut(RoleBase):
    id: int

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    email: EmailStr | None = None
    username: str
    full_name: str | None = None


class UserCreate(UserBase):
    password: str
    role_id: int


class UserUpdate(UserBase):
    password: str | None = None
    role_id: int | None = None
    is_active: bool | None = None
    is_locked: bool | None = None


class UserOut(UserBase):
    id: int
    is_active: bool
    is_locked: bool
    role: RoleOut

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: int
    action: str
    target_type: str | None
    target_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ===================== TABS / NAVIGATION =====================


class TabBase(BaseModel):
    path: str
    label: str
    sort_order: int | None = 0
    is_visible: bool | None = True
    icon: str | None = None


class TabCreate(TabBase):
    pass


class TabUpdate(BaseModel):
    path: str | None = None
    label: str | None = None
    sort_order: int | None = None
    is_visible: bool | None = None
    icon: str | None = None


class TabOut(TabBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
