# LocalLens Booking API

**Base URL:** `http://127.0.0.1:8000`

**Version:** `v1`

## Authentication

Send an `Authorization` header with booking requests. For requests with a JSON body, also send `Content-Type: application/json`.

```http
Authorization: Bearer user-a-token
Content-Type: application/json
```

| Account | Mock token | Access |
| --- | --- | --- |
| User A | `user-a-token` | Own bookings |
| User B | `user-b-token` | Own bookings |
| Admin | `admin-token` | All bookings |

Missing or invalid tokens should return `401 Unauthorized`. The examples below use `403 Forbidden` for access to someone else's booking because the caller is signed in but lacks permission. If we use `404 Not Found` instead, update the examples and document the reason after testing.

## Endpoint summary

| Method and path | Access | Input | Success | Possible errors |
| --- | --- | --- | --- | --- |
| `GET /api/v1/bookings` | Signed-in user or admin | Query: `page`, `perPage` | `200` | `400`, `401` |
| `GET /api/v1/bookings/{id}` | Booking owner or admin | Path: `id` | `200` | `400`, `401`, `403`, `404` |
| `POST /api/v1/bookings` | Signed-in user or admin | JSON body: `slotId` | `201` | `400`, `401` |
| `PUT /api/v1/bookings/{id}` | Booking owner or admin | Path: `id`. JSON body: `slotId` in the draft example | `200` | `400`, `401`, `403`, `404` |
| `DELETE /api/v1/bookings/{id}` | Booking owner or admin | Path: `id` | `200` in the draft example | `400`, `401`, `403`, `404` |
| `GET /api/v1/greeting` | Public | No parameters | `200` with HTML | `405` for unsupported methods |

Unsupported methods can also return `405` on booking paths. Document `409` if the team adds a booking conflict rule. Paths below use numeric booking IDs. Requests only use the inputs listed in the table.

## List bookings

**GET `/api/v1/bookings`**

A regular user sees only their own bookings. The admin sees the bookings of all users.

| Query parameter | Type | Default | Rules |
| --- | --- | --- | --- |
| `page` | integer | `1` | At least `1` |
| `perPage` | integer | `10` | From `1` to `50` |

The response includes `meta` with `total` (the number of bookings the caller can see, across all pages), `page` and `perPage`. A page past the end returns `200` with an empty `data` list.

**Errors:** `400 VALIDATION_ERROR` for an invalid `page` or `perPage` (for example `page=0`, `page=abc` or `perPage=51`), and `401 UNAUTHORIZED` for a missing or invalid token.

```http
GET /api/v1/bookings?page=1&perPage=1
Authorization: Bearer user-a-token
```

**200 OK**, example on a fresh run.

```json
{
  "success": true,
  "message": "Bookings retrieved.",
  "data": [
    {"id": 101, "slotId": 201, "ownerId": "user-a", "status": "confirmed"}
  ],
  "meta": {"total": 2, "page": 1, "perPage": 1}
}
```

## View a booking

**GET `/api/v1/bookings/{id}`**

The path parameter `id` is a positive integer that identifies a booking. User A can view booking `101`. The admin can view any booking. Use `999` to test the `404` case on a fresh run.

The API first checks that the booking exists and then checks access, so a missing booking always returns `404`.

**Errors:** `400 VALIDATION_ERROR` if `id` is not a positive integer (for example `abc` or `0`), `401 UNAUTHORIZED` for a missing or invalid token, `403 BOOKING_FORBIDDEN` if a regular user asks for another user's booking, and `404 BOOKING_NOT_FOUND` if no booking has this ID.

We return `403` rather than `404` for another user's booking because the caller is signed in and the booking exists, but they lack permission. This makes the reason for the failure clear while testing the prototype. Booking IDs are simple sequential numbers in the mock data and reveal nothing private.

```http
GET /api/v1/bookings/101
Authorization: Bearer user-a-token
```

**200 OK**

```json
{
  "success": true,
  "message": "Booking retrieved.",
  "data": {"id": 101, "slotId": 201, "ownerId": "user-a", "status": "confirmed"}
}
```

## Create a booking

**POST `/api/v1/bookings`**

The body must contain `slotId` as a positive JSON integer. Text, zero, negative numbers, missing values, and extra fields cause a validation error. The API assigns the booking ID and status. The API takes `ownerId` from the authenticated user.

```http
POST /api/v1/bookings
Authorization: Bearer user-a-token
Content-Type: application/json

{"slotId": 205}
```

**201 Created**, example for the first booking on a fresh run.

```json
{
  "success": true,
  "message": "Booking created.",
  "data": {"id": 105, "slotId": 205, "ownerId": "user-a", "status": "confirmed"}
}
```

With a valid token, sending `{"slotId": "205"}` returns **400 Bad Request** because `"205"` is a string.

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Check the submitted fields.",
    "details": [
      {"field": "slotId", "message": "Input should be a valid integer"}
    ]
  }
}
```

## Update a booking

**PUT `/api/v1/bookings/{id}`**

Moves a booking to another time slot. The path parameter `id` is a positive integer. The body must contain exactly one field, `slotId`, which is a positive JSON integer. The API never changes `id`, `ownerId` or `status` through this endpoint, so a body with any other field is rejected. The owner of the booking or the admin can update it.

```http
PUT /api/v1/bookings/101
Authorization: Bearer user-a-token
Content-Type: application/json

{"slotId": 206}
```

**200 OK**

```json
{
  "success": true,
  "message": "Booking updated.",
  "data": {"id": 101, "slotId": 206, "ownerId": "user-a", "status": "confirmed"}
}
```

**Errors:** `400 VALIDATION_ERROR` if `slotId` is missing, is not an integer (for example `"206"` or `2.5`), is zero or negative, or if the body has an extra field such as `ownerId`; `401 UNAUTHORIZED` for a missing or invalid token; `403 BOOKING_FORBIDDEN` if a regular user updates another user's booking; `404 BOOKING_NOT_FOUND` if no booking has this ID.

Example: sending `{"slotId": 206, "ownerId": "user-b"}` returns **400 Bad Request**.

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Check the submitted fields.",
    "details": [
      {"field": "ownerId", "message": "Extra inputs are not permitted"}
    ]
  }
}
```

Example: `PUT /api/v1/bookings/103` with `user-a-token` returns **403 Forbidden**.

```json
{
  "success": false,
  "error": {
    "code": "BOOKING_FORBIDDEN",
    "message": "You can access only your own bookings."
  }
}
```

## Delete a booking

**DELETE `/api/v1/bookings/{id}`**

The path parameter `id` identifies the booking to delete. The draft response uses `200` and `data: null`. Confirm the status and response with the delete implementation.

```http
DELETE /api/v1/bookings/102
Authorization: Bearer user-a-token
```

**200 OK**

```json
{
  "success": true,
  "message": "Booking deleted.",
  "data": null
}
```

## Open the greeting page

**GET `/api/v1/greeting`**

Open [the greeting page](http://127.0.0.1:8000/api/v1/greeting) in a browser. It shows the project description, team members, endpoint list, and API status and version.

```http
GET /api/v1/greeting
```

**200 OK**

```http
Content-Type: text/html; charset=utf-8
```

The response body is the LocalLens HTML page.

## Access and error examples

Use these requests to check the final access rules. Keep the error code and message consistent with the code after integration.

| Request | Expected result |
| --- | --- |
| `GET /api/v1/bookings/101` with no token or with an invalid token | `401 Unauthorized` |
| `GET /api/v1/bookings/103` with `user-a-token` | `403 Forbidden` |
| `GET /api/v1/bookings/103` with `admin-token` | `200 OK` |
| `GET /api/v1/bookings/999` with a valid token on a fresh run | `404 Not Found` |
| `PATCH /api/v1/bookings/101` with a valid token | `405 Method Not Allowed` |

Every error uses the same JSON format: `success: false` and an `error` object with a fixed `code` and a readable `message`. The `details` list appears only for validation errors.

| Status | `error.code` |
| --- | --- |
| `400` | `VALIDATION_ERROR` |
| `401` | `UNAUTHORIZED` |
| `403` | `BOOKING_FORBIDDEN` |
| `404` | `BOOKING_NOT_FOUND` |
| `405` | `HTTP_405` |

Example: a request with no token returns **401 Unauthorized**.

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "A valid bearer token is required."
  }
}
```