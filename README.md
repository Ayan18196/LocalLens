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

## Mock data

The app starts with four bookings in `mock_data.py`. Bookings `101` and `102` belong to User A. Bookings `103` and `104` belong to User B. Use ID `999` to test a booking that does not exist on a fresh run.

The bookings are stored in memory. When the server restarts, it reloads the original mock data and any changes from the previous run are lost.

## API examples and demo

- [API documentation and example requests](API.md)
- [LocalLens API Postman collection](postman/collections/LocalLens%20API/)
- YouTube demo: [add the video link, up to 5 minutes]

## Team contributions

| Team member | Work |
| --- | --- |
| Ayan Isgandarova | Set up FastAPI and the mock booking data, built the create-booking endpoint and its validation, and made the HTML greeting page. |
| Fatima Baghirli | Booking list, booking details, booking updates, pagination, and README instructions. |
| Nabati Hidayatov | Mock Bearer tokens, booking access checks, and the delete-booking endpoint. |

## Git contributions

Run `git shortlog -sn --all` from the project folder before submitting and paste the actual output below.

```text
[Paste git shortlog -sn --all output here]
```
