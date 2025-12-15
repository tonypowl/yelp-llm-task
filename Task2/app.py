from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import google.generativeai as genai
import json, os
from datetime import datetime

#loading env variables
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-flash-latest")
app = FastAPI()
templates = Jinja2Templates(directory="profile")

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_data(entry):
    data = load_data()
    data.append(entry)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def gemini_call(prompt, fallback):
    try:
        return model.generate_content(prompt).text
    except Exception:
        return fallback

#user dashboard
@app.get("/", response_class=HTMLResponse)
def user_dashboard(request: Request):
    return templates.TemplateResponse("user.html", {"request": request})

#submit button (post request)
@app.post("/submit", response_class=HTMLResponse)
def submit_review(
    request: Request,
    rating: int = Form(...),
    review: str = Form(...)
):
    ai_response = gemini_call(
        f"write a customer friendly response to this review:\n{review}",
        "Thanks for your feedback! kinda message nothing too long"
    )

    summary = gemini_call(
        f"summarize this review in one short sentence:\n{review}",
        "ex : customer shared positive feedback about their experience."
    )

    action = gemini_call(
        f"suggest one clear action that should be taken based on the review:\n{review}",
        "Review feedback and look for areas of improvement."
    )

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

#admin dashboard
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
