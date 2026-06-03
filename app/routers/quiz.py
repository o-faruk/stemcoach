from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from app.services.claude_service import generate_diagnostic_quiz
import json

router = APIRouter()


@router.post("/generate")
async def create_quiz(
    course_name: str = Form(...),
    topics: str = Form(...),  # JSON array of topic name strings
):
    """Generate a 10-question diagnostic quiz for the given topics."""
    try:
        topics_list = json.loads(topics)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid topics format.")

    if not topics_list:
        raise HTTPException(status_code=400, detail="At least one topic required.")

    quiz = generate_diagnostic_quiz(topics=topics_list, course_name=course_name)
    return JSONResponse(content=quiz)


@router.post("/score")
async def score_quiz(
    questions: str = Form(...),   # JSON array of question objects (with correct answers)
    answers: str = Form(...),     # JSON object: {question_id: "A"/"B"/"C"/"D"}
):
    """
    Score a completed quiz and return which topics the student struggled with.
    'Struggled' = got it wrong.
    """
    try:
        questions_list = json.loads(questions)
        answers_dict = json.loads(answers)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid format.")

    weak_topics = []
    results = []
    score = 0

    for q in questions_list:
        qid = str(q["id"])
        user_answer = answers_dict.get(qid, "").upper()
        correct = q["correct"].upper()
        is_correct = user_answer == correct

        if is_correct:
            score += 1
        else:
            if q["topic"] not in weak_topics:
                weak_topics.append(q["topic"])

        results.append({
            "id": q["id"],
            "topic": q["topic"],
            "correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": correct,
            "explanation": q.get("explanation", ""),
        })

    return JSONResponse(content={
        "score": score,
        "total": len(questions_list),
        "percentage": round(score / len(questions_list) * 100),
        "weak_topics": weak_topics,
        "results": results,
    })
