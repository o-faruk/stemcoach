from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from app.services.claude_service import chat_with_tutor
from app.services.pdf_service import extract_text_from_pdf, clean_text
import json

router = APIRouter()


@router.post("/start")
async def start_session(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    course_name: str = Form("My Course"),
    weak_topics: str = Form("[]"),
):
    """Start a tutor session. Returns opening message from tutor."""
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide a PDF or paste some text.")

    if file:
        file_bytes = await file.read()
        raw_text = extract_text_from_pdf(file_bytes)
        material_text = clean_text(raw_text)
    else:
        material_text = text

    if len(material_text) < 50:
        raise HTTPException(status_code=400, detail="Material too short.")

    try:
        weak_list = json.loads(weak_topics)
    except:
        weak_list = []

    weak_summary = ", ".join(weak_list) if weak_list else "none"

    opening = chat_with_tutor(
        message=f"Hi! I just uploaded my {course_name} material. My weak topics are: {weak_summary}. Can you start by giving me a quick overview of what we should focus on, then start quizzing me?",
        chat_history=[],
        material_text=material_text,
        course_name=course_name,
        weak_topics=weak_list,
    )

    return JSONResponse(content={
        "message": opening,
        "material_text": material_text[:8000],
    })


@router.post("/chat")
async def chat(
    message: str = Form(...),
    chat_history: str = Form("[]"),
    material_text: str = Form(...),
    course_name: str = Form("My Course"),
    weak_topics: str = Form("[]"),
):
    """Send a message and get a tutor response."""
    try:
        history = json.loads(chat_history)
        weak_list = json.loads(weak_topics)
    except:
        history = []
        weak_list = []

    response = chat_with_tutor(
        message=message,
        chat_history=history,
        material_text=material_text,
        course_name=course_name,
        weak_topics=weak_list,
    )

    return JSONResponse(content={"message": response})
