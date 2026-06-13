from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from app.services.claude_service import extract_topics_from_syllabus, generate_study_plan
from app.services.pdf_service import extract_text_from_pdf, clean_text

router = APIRouter()


@router.post("/upload-syllabus")
async def upload_syllabus(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
):
    """Accept a PDF upload or raw pasted text. Returns extracted topics."""
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide a PDF file or paste syllabus text.")

    if file:
        content = await file.read()
        raw_text = extract_text_from_pdf(content)
        syllabus_text = clean_text(raw_text)
    else:
        syllabus_text = text

    if len(syllabus_text) < 50:
        raise HTTPException(status_code=400, detail="Syllabus text too short to analyze.")

    topics_data = extract_topics_from_syllabus(syllabus_text[:8000])  # cap tokens
    return JSONResponse(content=topics_data)


@router.post("/generate")
async def create_study_plan(
    course_name: str = Form(...),
    topics: str = Form(...),         # JSON string of topic objects
    weak_topics: str = Form(...),    # JSON string of topic name strings
    days_available: int = Form(14),
    hours_per_day: float = Form(2.0),
    exam_date: Optional[str] = Form(None),
):
    """Generate a personalized study plan based on topics and weak spots."""
    import json
    try:
        topics_list = json.loads(topics)
        weak_list = json.loads(weak_topics)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid topics format.")

    plan = generate_study_plan(
        course_name=course_name,
        topics=topics_list,
        weak_topics=weak_list,
        days_available=days_available,
        hours_per_day=hours_per_day,
        exam_date=exam_date,
    )
    return JSONResponse(content=plan)
from app.services.claude_service import analyze_past_exam, generate_exam_focused_study_plan


@router.post("/upload-exam")
async def upload_exam(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    course_name: str = Form("My Course"),
):
    """Accept a past exam PDF or text. Returns analyzed topics weighted by exam frequency."""
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide a PDF file or paste exam text.")

    if file:
        file_bytes = await file.read()
        raw_text = extract_text_from_pdf(file_bytes)
        exam_text = clean_text(raw_text)
    else:
        exam_text = text

    if len(exam_text) < 50:
        raise HTTPException(status_code=400, detail="Exam text too short to analyze.")

    exam_data = analyze_past_exam(exam_text[:8000], course_name)
    return JSONResponse(content=exam_data)


@router.post("/generate-exam-focused")
async def create_exam_focused_plan(
    course_name: str = Form(...),
    topics: str = Form(...),
    weak_topics: str = Form(...),
    high_priority_topics: str = Form(...),
    exam_insights: str = Form(...),
    days_available: int = Form(14),
    hours_per_day: float = Form(2.0),
):
    """Generate a study plan optimized for a specific past exam."""
    import json
    try:
        topics_list = json.loads(topics)
        weak_list = json.loads(weak_topics)
        priority_list = json.loads(high_priority_topics)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid format.")

    plan = generate_exam_focused_study_plan(
        course_name=course_name,
        topics=topics_list,
        weak_topics=weak_list,
        high_priority_topics=priority_list,
        exam_insights=exam_insights,
        days_available=days_available,
        hours_per_day=hours_per_day,
    )
    return JSONResponse(content=plan)
