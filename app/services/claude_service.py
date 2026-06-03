from groq import Groq
import os
import json
from typing import Optional

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _chat(prompt: str, max_tokens: int = 1500) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def extract_topics_from_syllabus(syllabus_text: str) -> dict:
    prompt = f"""You are an expert STEM academic advisor. Analyze this syllabus and extract key topics.

Syllabus:
{syllabus_text}

Return a JSON object with this exact structure (no markdown, just raw JSON):
{{
  "course_name": "string",
  "topics": [
    {{
      "name": "string",
      "week": null,
      "difficulty": "low" | "medium" | "high",
      "prerequisites": ["topic names that come before this"]
    }}
  ]
}}"""
    return _parse_json(_chat(prompt, max_tokens=1500))


def generate_diagnostic_quiz(topics: list[str], course_name: str) -> dict:
    topics_str = ", ".join(topics[:15])
    prompt = f"""You are a STEM professor creating a diagnostic quiz to find a student's weak spots.

Course: {course_name}
Topics to cover: {topics_str}

Create exactly 10 multiple-choice questions. Spread them across the topics. Make them conceptual, not just memorization.

Return a JSON object (no markdown, raw JSON only):
{{
  "questions": [
    {{
      "id": 1,
      "topic": "topic name this tests",
      "question": "question text",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct": "A",
      "explanation": "brief explanation of why this is correct"
    }}
  ]
}}"""
    return _parse_json(_chat(prompt, max_tokens=2500))


def generate_study_plan(
    course_name: str,
    topics: list[dict],
    weak_topics: list[str],
    days_available: int = 14,
    hours_per_day: float = 2.0,
    exam_date: Optional[str] = None,
) -> dict:
    topics_summary = "\n".join(
        [f"- {t['name']} (difficulty: {t.get('difficulty','medium')})" for t in topics]
    )
    weak_summary = ", ".join(weak_topics) if weak_topics else "none identified"
    exam_context = f"Exam date: {exam_date}" if exam_date else f"Planning for {days_available} days"

    prompt = f"""You are an expert STEM tutor building a personalized study plan.

Course: {course_name}
{exam_context}
Hours available per day: {hours_per_day}

All course topics:
{topics_summary}

Topics the student struggled with (prioritize these):
{weak_summary}

Build a realistic day-by-day study plan. Weak topics get more time. Build from fundamentals up.
Include specific actions, not just topic names. Keep it achievable.

Return JSON only (no markdown):
{{
  "summary": "2-3 sentence overview of the strategy",
  "total_hours": 0,
  "days": [
    {{
      "day": 1,
      "date_offset": "Day 1",
      "focus_topic": "main topic",
      "hours": 2,
      "tasks": [
        {{
          "task": "specific action",
          "duration_minutes": 30,
          "resource_type": "lecture"
        }}
      ],
      "goal": "what the student should be able to do after today"
    }}
  ]
}}"""
    return _parse_json(_chat(prompt, max_tokens=3000))