from fastapi import APIRouter, Depends, Query

from auth import get_current_user
from mock_data import bookings

router = APIRouter()


def visible_bookings(user: dict) -> list:
    if user["role"] == "admin":
        return list(bookings)
    return [booking for booking in bookings if booking["ownerId"] == user["id"]]


def paginate(items: list, page: int, per_page: int) -> list:
    start = (page - 1) * per_page
    return items[start:start + per_page]


@router.get("/api/v1/bookings")
def list_bookings(
    page: int = Query(1, gt=0),
    perPage: int = Query(10, gt=0, le=50),
    user: dict = Depends(get_current_user),
):
    items = visible_bookings(user)

    return {
        "success": True,
        "message": "Bookings retrieved.",
        "data": paginate(items, page, perPage),
        "meta": {"total": len(items), "page": page, "perPage": perPage},
    }