# LocalLens

LocalLens helps travelers find and book local experiences. This FastAPI prototype uses bookings as its main resource. It also has an HTML greeting page with the team details and endpoint list.

## How to run the project

Install Python 3 and open the LocalLens project folder in a terminal.

**Windows (PowerShell)**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

**macOS or Linux**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn main:app --reload
```

Keep the server running while you open these pages:

- [API greeting page](http://127.0.0.1:8000/api/v1/greeting)
- [Interactive API documentation](http://127.0.0.1:8000/docs)

## Authentication

There is no real login. Every booking request must send one of three mock tokens in the `Authorization` header:

```http
Authorization: Bearer user-a-token
```

| Account | Token | Access |
| --- | --- | --- |
| User A | `user-a-token` | Only User A's bookings |
| User B | `user-b-token` | Only User B's bookings |
| Admin | `admin-token` | All bookings |

A missing or wrong token returns `401 Unauthorized`. A regular user who tries to view or change another user's booking gets `403 Forbidden`.

To use a token in the interactive documentation at `/docs`, click **Authorize** and paste only the token, for example `user-a-token`.

## Running the tests

With the virtual environment set up as above, run:

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

**macOS or Linux**

```bash
.venv/bin/python -m pytest -v
```

The tests in `test_bookings.py` cover listing with pagination, viewing and updating bookings, validation errors, missing and invalid tokens, access to another user's booking, and admin access. Each test starts from the original mock data.

## Mock data

The app starts with four bookings in `mock_data.py`. Bookings `101` and `102` belong to User A. Bookings `103` and `104` belong to User B. Use ID `999` to test a booking that does not exist on a fresh run.

The bookings are stored in memory. When the server restarts, it reloads the original mock data and any changes from the previous run are lost.

## API examples and demo

- [API documentation and example requests](API.md)
- [LocalLens API Postman collection](postman/collections/LocalLens%20API/)
- YouTube demo: https://www.youtube.com/watch?v=AX46yOZjQWc

## Team contributions

| Team member | Work |
| --- | --- |
| Ayan Isgandarova | Set up FastAPI and the mock booking data, built the create-booking endpoint and its validation, and made the HTML greeting page. |
| Fatima Baghirli | Booking list, booking details, booking updates, pagination, the JSON error format, tests, README instructions, API documentation for her endpoints, and the demo video. |
| Nabati Hidayatov | Mock Bearer tokens, booking access checks, and the delete-booking endpoint. |

## Git contributions

Output of `git shortlog -sn --all`:

```text
    20	Ayan18196
    15	Fatima Baghirli
     3	Nabati Hidayatov
     1	Nabati-Hidayatov
     1	fatimamb-blip
```

Some people appear twice because their Git name was set differently on some commits:

- `Fatima Baghirli` and `fatimamb-blip` are both Fatima Baghirli.
- `Nabati Hidayatov` and `Nabati-Hidayatov` are both Nabati Hidayatov.

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for each member's student ID and responsibilities.