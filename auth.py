from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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
