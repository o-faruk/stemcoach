import anthropic
import os
from typing import Optional

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def extract_topics_from_syllabus(syllabus_text: str) -> dict:
    """
    Takes raw syllabus text and returns structured topics with difficulty weights.
    """
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert STEM academic advisor. Analyze this syllabus and extract key topics.

Syllabus:
{syllabus_text}

Return a JSON object with this exact structure (no markdown, just raw JSON):
{{
  "course_name": "string",
  "topics": [
    {{
      "name": "string",
      "week": number or null,
      "difficulty": "low" | "medium" | "high",
      "prerequisites": ["topic names that come before this"]
    }}
  ]
}}

Difficulty should reflect how conceptually demanding the topic typically is for students.""",
            }
        ],
    )
    import json
    raw = message.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_diagnostic_quiz(topics: list[str], course_name: str) -> dict:
    """
    Generates a 10-question diagnostic quiz for the given topics.
    """
    topics_str = ", ".join(topics[:15])  # cap at 15 topics
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2500,
        messages=[
            {
                "role": "user",
                "content": f"""You are a STEM professor creating a diagnostic quiz to find a student's weak spots.

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
}}""",
            }
        ],
    )
    import json
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_study_plan(
    course_name: str,
    topics: list[dict],
    weak_topics: list[str],
    days_available: int = 14,
    hours_per_day: float = 2.0,
    exam_date: Optional[str] = None,
) -> dict:
    """
    Generates a personalized day-by-day study plan prioritizing weak spots.
    """
    topics_summary = "\n".join(
        [f"- {t['name']} (difficulty: {t.get('difficulty','medium')})" for t in topics]
    )
    weak_summary = ", ".join(weak_topics) if weak_topics else "none identified"

    exam_context = f"Exam date: {exam_date}" if exam_date else f"Planning for {days_available} days"

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=3000,
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert STEM tutor building a personalized study plan.

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
  "total_hours": number,
  "days": [
    {{
      "day": 1,
      "date_offset": "Day 1",
      "focus_topic": "main topic",
      "hours": number,
      "tasks": [
        {{
          "task": "specific action (e.g. Re-watch lecture 3 on integration by parts)",
          "duration_minutes": number,
          "resource_type": "lecture" | "practice" | "review" | "reading"
        }}
      ],
      "goal": "what the student should be able to do after today"
    }}
  ]
}}""",
            }
        ],
    )
    import json
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
