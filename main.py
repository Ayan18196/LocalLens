from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse

from starlette.exceptions import HTTPException as StarletteHTTPException

from booking_create import BookingRequest, create_booking

app = FastAPI(title="LocalLens API")

ERROR_CODES = {
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
}


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

@app.exception_handler(StarletteHTTPException)
async def handle_http_error(_request, error: StarletteHTTPException):
    response = {
        "success": False,
        "error": {
            "code": ERROR_CODES.get(error.status_code, "ERROR"),
            "message": str(error.detail),
        },
    }

    return JSONResponse(
        status_code=error.status_code,
        content=response,
        headers=getattr(error, "headers", None),
    )


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


@app.get("/api/v1/greeting", response_class=HTMLResponse)
def greeting():
    page = Path(__file__).with_name("greeting.html")
    return page.read_text(encoding="utf-8")