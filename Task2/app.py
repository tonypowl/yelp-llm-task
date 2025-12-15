from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
import json, os
from datetime import datetime

# Gemini setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-flash-latest")

app = FastAPI()
templates = Jinja2Templates(directory="profile")

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(entry):
    data = load_data()
    data.append(entry)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------- USER DASHBOARD ----------------

@app.get("/", response_class=HTMLResponse)
def user_dashboard(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})


@app.post("/submit", response_class=HTMLResponse)
def submit_review(
    request: Request,
    rating: int = Form(...),
    review: str = Form(...)
):
    ai_response = model.generate_content(
        f"Write a friendly response to this customer review:\n{review}"
    ).text

    summary = model.generate_content(
        f"Summarize this review in one short sentence:\n{review}"
    ).text

    action = model.generate_content(
        f"Suggest one clear action a business should take based on this review:\n{review}"
    ).text

    save_data({
        "rating": rating,
        "review": review,
        "ai_response": ai_response,
        "summary": summary,
        "action": action,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "ai_response": ai_response
        }
    )


# ---------------- ADMIN DASHBOARD ----------------

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    data = load_data()
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "data": data
        }
    )
