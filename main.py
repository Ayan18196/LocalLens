from fastapi import FastAPI
from pathlib import Path
from fastapi.responses import HTMLResponse

app = FastAPI(title="LocalLens API")

@app.get("/api/v1/greeting", response_class=HTMLResponse)
def greeting():
    page = Path(__file__).with_name("greeting.html")
    return page.read_text(encoding="utf-8")