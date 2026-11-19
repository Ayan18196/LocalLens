from itertools import count

from mock_data import bookings

from pydantic import BaseModel, ConfigDict, Field


class BookingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slotId: int = Field(strict=True, gt=0)

existing_ids = [booking["id"] for booking in bookings]
next_booking_id = count(max(existing_ids, default=0) + 1)


def create_booking(slot_id: int, owner_id: str):
    booking = {
        "id": next(next_booking_id),
        "slotId": slot_id,
        "ownerId": owner_id,
        "status": "confirmed",
    }

    bookings.append(booking)
    return booking