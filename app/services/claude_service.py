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
    """Takes raw syllabus text and returns structured topics with difficulty weights."""
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
}}

Difficulty should reflect how conceptually demanding the topic typically is for students."""
    return _parse_json(_chat(prompt, max_tokens=1500))


def generate_diagnostic_quiz(topics: list[str], course_name: str) -> dict:
    """Generates a 10-question diagnostic quiz for the given topics."""
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
    """Generates a personalized day-by-day study plan prioritizing weak spots."""
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
          "task": "specific action (e.g. Re-watch lecture 3 on integration by parts)",
          "duration_minutes": 30,
          "resource_type": "lecture"
        }}
      ],
      "goal": "what the student should be able to do after today"
    }}
  ]
}}"""
    return _parse_json(_chat(prompt, max_tokens=3000))


def analyze_past_exam(exam_text: str, course_name: str) -> dict:
    """
    Analyzes a past exam to extract topics, question patterns, and difficulty.
    Returns weighted topics based on how heavily they were tested.
    """
    prompt = f"""You are an expert STEM academic advisor analyzing a past exam.

Course: {course_name}
Past Exam:
{exam_text}

Analyze this exam and extract what topics were tested and how heavily.

Return JSON only (no markdown):
{{
  "course_name": "{course_name}",
  "exam_insights": "2-3 sentence summary of what this exam focused on",
  "topics": [
    {{
      "name": "topic name",
      "question_count": 1,
      "difficulty": "low",
      "question_types": ["conceptual"],
      "prerequisites": []
    }}
  ],
  "high_priority_topics": ["topics that appeared most on the exam"],
  "exam_style": "mixed"
}}"""
    return _parse_json(_chat(prompt, max_tokens=2000))


def generate_exam_focused_study_plan(
    course_name: str,
    topics: list[dict],
    weak_topics: list[str],
    high_priority_topics: list[str],
    exam_insights: str,
    days_available: int = 14,
    hours_per_day: float = 2.0,
) -> dict:
    """
    Generates a study plan optimized for a specific past exam pattern.
    """
    topics_summary = "\n".join(
        [f"- {t['name']} (appeared {t.get('question_count', 1)}x, difficulty: {t.get('difficulty','medium')})" for t in topics]
    )
    weak_summary = ", ".join(weak_topics) if weak_topics else "none identified"
    priority_summary = ", ".join(high_priority_topics) if high_priority_topics else "none"

    prompt = f"""You are an expert STEM tutor building a study plan optimized for a specific exam.

Course: {course_name}
Exam insights: {exam_insights}
Planning for: {days_available} days, {hours_per_day} hours/day

Topics from past exam (with frequency):
{topics_summary}

Student weak topics: {weak_summary}
High priority topics (appeared most): {priority_summary}

Build a study plan that heavily prioritizes topics that appeared most on the exam.

Return JSON only (no markdown):
{{
  "summary": "2-3 sentence strategy overview",
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
          "resource_type": "practice"
        }}
      ],
      "goal": "what student should achieve today"
    }}
  ]
}}"""
    return _parse_json(_chat(prompt, max_tokens=3000))


def generate_tutor_question(
    material_text: str,
    course_name: str,
    weak_topics: list[str],
    question_history: list[dict],
    difficulty: str = "medium"
) -> dict:
    """
    Generates a tutor question based on uploaded material.
    Adapts difficulty based on student performance.
    """
    history_summary = ""
    if question_history:
        history_summary = "Previous questions asked:\n" + "\n".join(
            [f"- {q['question']} (student got: {q['result']})" for q in question_history[-5:]]
        )

    weak_summary = ", ".join(weak_topics) if weak_topics else "none identified"

    prompt = f"""You are a STEM tutor conducting an oral exam session. You have the student's course material in front of you.

Course: {course_name}
Student's weak topics: {weak_summary}
Current difficulty level: {difficulty}

Course material:
{material_text[:6000]}

{history_summary}

Generate ONE question to ask the student. Rules:
- Base it directly on the material provided
- If student has weak topics, prioritize those
- Match the difficulty level ({difficulty})
- For medium/hard: ask them to explain a concept or solve a problem
- For easy: ask them to define or describe something basic
- Don't repeat previous questions
- Make it specific enough that you can grade their answer

Return JSON only (no markdown):
{{
  "question": "the question to ask",
  "topic": "which topic this tests",
  "difficulty": "{difficulty}",
  "ideal_answer_points": ["key point 1", "key point 2", "key point 3"],
  "hint": "a subtle hint if they get stuck"
}}"""
    return _parse_json(_chat(prompt, max_tokens=1000))


def grade_student_answer(
    question: str,
    ideal_points: list[str],
    student_answer: str,
    course_name: str,
    topic: str,
) -> dict:
    """
    Grades a student's answer and provides detailed feedback.
    """
    points_str = "\n".join([f"- {p}" for p in ideal_points])

    prompt = f"""You are a STEM professor grading a student's oral exam answer.

Course: {course_name}
Topic: {topic}
Question asked: {question}

Key points a good answer should cover:
{points_str}

Student's answer: {student_answer}

Grade their answer fairly. Be encouraging but honest. If they're partially right, acknowledge what they got right before correcting.

Return JSON only (no markdown):
{{
  "grade": "correct" | "partial" | "incorrect",
  "score": 0-100,
  "feedback": "2-3 sentences of specific feedback on their answer",
  "what_they_got_right": "what was good about their answer (empty string if nothing)",
  "corrections": "what was wrong or missing (empty string if nothing)",
  "full_explanation": "complete explanation of the correct answer in 3-4 sentences",
  "encouragement": "one encouraging sentence to keep them going"
}}"""
    return _parse_json(_chat(prompt, max_tokens=1200))


def chat_with_tutor(
    message: str,
    chat_history: list[dict],
    material_text: str,
    course_name: str,
    weak_topics: list[str],
) -> str:
    """
    Full conversational tutor. Has the course material as context.
    Can answer questions, quiz the student, give feedback, and adapt.
    """
    weak_summary = ", ".join(weak_topics) if weak_topics else "none identified"
    
    history_str = ""
    for msg in chat_history[-12:]:
        role = "Student" if msg["role"] == "user" else "Tutor"
        history_str += f"{role}: {msg['content']}\n\n"

    prompt = f"""You are an expert STEM tutor having a conversation with a student. You have their course material in front of you.

Course: {course_name}
Student weak topics: {weak_summary}

Course material:
{material_text[:5000]}

Conversation so far:
{history_str}
Student: {message}

Respond as a knowledgeable, encouraging tutor. You can:
- Answer their questions directly using the material
- Ask them follow-up questions to test understanding
- Quiz them on weak topics when appropriate
- Give examples, analogies, or worked problems
- Correct misconceptions clearly but kindly
- Praise correct answers and explain wrong ones

Keep responses focused and conversational. Don't be overly long. If they ask you to quiz them, ask one question at a time and wait for their answer before moving on.

Tutor:"""
    
    response = _chat(prompt, max_tokens=800)
    return response.strip()
