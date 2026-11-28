from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    StringConstraints,
    field_validator,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from database import get_db
from models import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
password_hash = PasswordHash.recommended()


class RegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=1, max_length=100, pattern=r"^[^\x00]+$"
        ),
    ]
    email: EmailStr
    password: SecretStr = Field(min_length=15, max_length=128)
    role: Literal["customer", "host"]

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        normalized_email = email.lower()
        if len(normalized_email) > 255:
            raise ValueError("Email must be at most 255 characters.")
        return normalized_email


MOCK_USERS = {
    "user-a-token": {"id": "user-a", "role": "user"},
    "user-b-token": {"id": "user-b", "role": "user"},
    "admin-token": {"id": "admin", "role": "admin"},
}
bearer_scheme = HTTPBearer(auto_error=False)
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    user = None
    if credentials is not None:
        token = credentials.credentials
        user = MOCK_USERS.get(token)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "UNAUTHORIZED",
                "message": "A valid bearer token is required.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
def get_booking_owner(user: dict = Depends(get_current_user)) -> str:
    return user["id"]
def require_booking_access(booking: dict, user: dict) -> None:
    is_admin = user["role"] == "admin"
    is_owner = booking["ownerId"] == user["id"]

    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "BOOKING_FORBIDDEN",
                "message": "You can access only your own bookings.",
            },
        )


@router.post("/register", status_code=201)
def register(request: RegistrationRequest, db: Annotated[Session, Depends(get_db)]):
    approval_status = "pending" if request.role == "host" else "approved"
    statement = (
        insert(User)
        .values(
            name=request.name,
            email=request.email,
            password_hash=password_hash.hash(request.password.get_secret_value()),
            role=request.role,
            approval_status=approval_status,
        )
        .on_conflict_do_nothing(index_elements=[User.email])
        .returning(User.id)
    )
    with db.begin():
        user_id = db.scalar(statement)
        if user_id is None:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "CONFLICT",
                    "message": "An account with this email already exists.",
                },
            )

    return {
        "success": True,
        "message": "Account created.",
        "data": {
            "id": user_id,
            "name": request.name,
            "email": request.email,
            "role": request.role,
            "approvalStatus": approval_status,
        },
    }
