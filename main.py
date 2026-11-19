from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from booking_create import BookingRequest, create_booking

app = FastAPI(title="LocalLens API")


def get_booking_owner() -> str:
    raise HTTPException(status_code=401, detail="A valid token is required.")


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_request, error: RequestValidationError):
    details = []

    for item in error.errors():
        # Skip the first part of the location, such as "body".
        field_parts = item["loc"][1:]
        field_name = ".".join(str(part) for part in field_parts)

        details.append({
            "field": field_name or "body",
            "message": item["msg"],
        })

    response = {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Check the submitted fields.",
            "details": details,
        },
    }

    return JSONResponse(status_code=400, content=response)


@app.post("/api/v1/bookings", status_code=201)
async def post_booking(
    booking: BookingRequest,
    owner_id: str = Depends(get_booking_owner),
):
    new_booking = create_booking(booking.slotId, owner_id)

    return {
        "success": True,
        "message": "Booking created.",
        "data": new_booking,
    }