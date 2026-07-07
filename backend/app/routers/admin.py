from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from ..database import SessionLocal
from ..models import Role, Tab, User
from ..schemas import (
    RoleCreate,
    RoleOut,
    TabCreate,
    TabOut,
    TabUpdate,
    UserCreate,
    UserOut,
    UserUpdate,
)
from .auth import get_password_hash, require_roles

router = APIRouter()


def _get_user_or_404(user_id: int) -> User:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    finally:
        db.close()


def _get_tab_or_404(tab_id: int) -> Tab:
    db = SessionLocal()
    try:
        tab = db.query(Tab).filter(Tab.id == tab_id).first()
        if not tab:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tab not found")
        return tab
    finally:
        db.close()


class RolesResponse(BaseModel):
    roles: list[RoleOut]


@router.get("/admin/roles", response_model=RolesResponse)
def list_roles(_: User = Depends(require_roles("admin"))):
    db = SessionLocal()
    try:
        roles = db.query(Role).order_by(Role.name.asc()).all()
        return RolesResponse(roles=roles)
    finally:
        db.close()


@router.post("/admin/roles", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, _: User = Depends(require_roles("admin"))):
    db = SessionLocal()
    try:
        role = Role(**payload.model_dump())
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    finally:
        db.close()


class UsersResponse(BaseModel):
    users: list[UserOut]
    total: int


@router.get("/admin/users", response_model=UsersResponse)
def list_users(
    q: str | None = Query(default=None),
    active: bool | None = Query(default=None),
    _: User = Depends(require_roles("admin")),
):
    db = SessionLocal()
    try:
        query = db.query(User)
        if q:
            query = query.filter(User.username.ilike(f"%{q}%"))
        if active is not None:
            query = query.filter(User.is_active == active)
        users = query.order_by(User.id.asc()).all()
        return UsersResponse(users=users, total=len(users))
    finally:
        db.close()


@router.post("/admin/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, _: User = Depends(require_roles("admin"))):
    db = SessionLocal()
    try:
        user = User(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            role_id=payload.role_id,
            hashed_password=get_password_hash(payload.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


@router.patch("/admin/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    _: User = Depends(require_roles("admin")),
):
    user = _get_user_or_404(user_id)
    db = SessionLocal()
    try:
        updates = payload.model_dump(exclude_unset=True)
        if "password" in updates:
            user.hashed_password = get_password_hash(updates.pop("password"))
        for k, v in updates.items():
            setattr(user, k, v)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    _: User = Depends(require_roles("admin")),
):
    user = _get_user_or_404(user_id)
    db = SessionLocal()
    try:
        db.delete(user)
        db.commit()
    finally:
        db.close()


class TabsResponse(BaseModel):
    tabs: list[TabOut]


@router.get("/admin/tabs", response_model=TabsResponse)
def list_tabs(_: User = Depends(require_roles("admin"))):
    db = SessionLocal()
    try:
        tabs = db.query(Tab).order_by(Tab.sort_order.asc(), Tab.id.asc()).all()
        return TabsResponse(tabs=tabs)
    finally:
        db.close()


@router.post("/admin/tabs", response_model=TabOut, status_code=status.HTTP_201_CREATED)
def create_tab(payload: TabCreate, _: User = Depends(require_roles("admin"))):
    db = SessionLocal()
    try:
        tab = Tab(**payload.model_dump())
        db.add(tab)
        db.commit()
        db.refresh(tab)
        return tab
    finally:
        db.close()


@router.patch("/admin/tabs/{tab_id}", response_model=TabOut)
def update_tab(
    tab_id: int,
    payload: TabUpdate,
    _: User = Depends(require_roles("admin")),
):
    tab = _get_tab_or_404(tab_id)
    db = SessionLocal()
    try:
        updates = payload.model_dump(exclude_unset=True)
        for k, v in updates.items():
            setattr(tab, k, v)
        db.add(tab)
        db.commit()
        db.refresh(tab)
        return tab
    finally:
        db.close()


@router.delete("/admin/tabs/{tab_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tab(
    tab_id: int,
    _: User = Depends(require_roles("admin")),
):
    tab = _get_tab_or_404(tab_id)
    db = SessionLocal()
    try:
        db.delete(tab)
        db.commit()
    finally:
        db.close()
