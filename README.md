# STEMCoach — AI Study Coach for STEM Students

## Setup (do this first)

### 1. Clone and enter the project
```bash
cd stemcoach
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Then open `.env` and fill in your keys:
- **ANTHROPIC_API_KEY** — get from https://console.anthropic.com
- **SUPABASE_URL / SUPABASE_ANON_KEY** — get from https://supabase.com (free tier)
- **STRIPE_*** — get from https://dashboard.stripe.com (use test mode keys first)

### 5. Run the dev server
```bash
uvicorn main:app --reload
```

Open http://localhost:8000 — you should see the landing page.

---

## Project Structure

```
stemcoach/
├── main.py                        # FastAPI app entry point
├── requirements.txt
├── .env.example
├── app/
│   ├── routers/
│   │   ├── study_plan.py          # /study-plan/* endpoints
│   │   ├── quiz.py                # /quiz/* endpoints
│   │   ├── auth.py                # /auth/* endpoints (Supabase stub)
│   │   └── billing.py             # /billing/* endpoints (Stripe)
│   ├── services/
│   │   ├── claude_service.py      # All Anthropic API calls
│   │   └── pdf_service.py         # PDF text extraction
│   ├── templates/
│   │   ├── index.html             # Landing page
│   │   └── dashboard.html         # User dashboard (stub)
│   └── static/
│       └── css/                   # Add custom CSS here
└── tests/                         # Add tests here
```

---

## API Endpoints

| Method | Path | What it does |
|--------|------|-------------|
| POST | /study-plan/upload-syllabus | Upload PDF or text → returns topics |
| POST | /study-plan/generate | Topics + weak spots → study plan |
| POST | /quiz/generate | Topics → 10-question diagnostic quiz |
| POST | /quiz/score | Student answers → score + weak topics |
| POST | /billing/create-checkout-session | Start Stripe checkout |
| POST | /billing/webhook | Handle Stripe events |

Interactive API docs: http://localhost:8000/docs

---

## Build Order (recommended)

1. Get `/study-plan/upload-syllabus` working end-to-end
2. Get `/quiz/generate` + `/quiz/score` working
3. Chain them: syllabus → quiz → study plan
4. Wire Supabase auth
5. Wire Stripe billing
6. Build the dashboard UI
