from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from supabase import create_client
import os

router = APIRouter()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)


@router.post("/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            return JSONResponse(content={"message": "Check your email to confirm your account.", "user_id": str(res.user.id)})
        raise HTTPException(status_code=400, detail="Signup failed.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            return JSONResponse(content={
                "access_token": res.session.access_token,
                "user_id": str(res.user.id),
                "email": res.user.email,
            })
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
async def logout():
    try:
        supabase.auth.sign_out()
        return JSONResponse(content={"message": "Logged out."})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def get_me(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    try:
        user = supabase.auth.get_user(token)
        return JSONResponse(content={"user_id": str(user.user.id), "email": user.user.email})
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token.")