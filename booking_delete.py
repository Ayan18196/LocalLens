from fastapi import APIRouter, Depends, HTTPException, Path
from auth import get_current_user, require_booking_access
from mock_data import bookings
router = APIRouter()
@router.delete("/api/v1/bookings/{id}")
def delete_booking(
    id: int = Path(gt=0),
    user: dict = Depends(get_current_user),
):
    booking = None
    for item in bookings:
        if item["id"] == id:
            booking = item
            break
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "BOOKING_NOT_FOUND",
                "message": "Booking not found.",
            },
        )
    require_booking_access(booking, user)
    bookings.remove(booking)
    return {
        "success": True,
        "message": "Booking deleted.",
        "data": None,
    }
