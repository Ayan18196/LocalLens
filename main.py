from pathlib import Path
from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException
from auth import get_booking_owner
from booking_create import BookingRequest, create_booking
from booking_delete import router as booking_delete_router
app = FastAPI(title="LocalLens API")
app.include_router(booking_delete_router)
@app.exception_handler(HTTPException)
async def handle_http_error(_request, error: HTTPException):
    detail = error.detail
    if not isinstance(detail, dict):
        detail = {
            "code": f"HTTP_{error.status_code}",
            "message": str(detail),
        }
    return JSONResponse(
        status_code=error.status_code,
        content={"success": False, "error": detail},
        headers=error.headers,
    )
@app.exception_handler(RequestValidationError)
async def handle_validation_error(_request, error: RequestValidationError):
    details = []
    for item in error.errors():
        # Remove the location prefix, such as "body", to get the field name.
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
@app.get("/api/v1/greeting", response_class=HTMLResponse)
def greeting():
    page = Path(__file__).with_name("greeting.html")
    return page.read_text(encoding="utf-8")
