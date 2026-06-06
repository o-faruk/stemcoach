from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from app.routers import study_plan, quiz, auth, billing

app = FastAPI(title="STEM Study Coach", version="0.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(study_plan.router, prefix="/study-plan", tags=["study-plan"])
app.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/health")
async def health():
    return {"status": "ok"}
