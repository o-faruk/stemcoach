from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
import os

router = APIRouter()

# NOTE: Wire up Supabase client here once you have credentials.
# For now these are placeholder endpoints so the app structure is complete.
# pip install supabase, then:
# from supabase import create_client
# supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))


@router.post("/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    """Create a new user account via Supabase Auth."""
    # TODO: supabase.auth.sign_up({"email": email, "password": password})
    return JSONResponse(content={"message": "Signup endpoint — wire up Supabase here."})


@router.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    """Log in and return a session token."""
    # TODO: supabase.auth.sign_in_with_password({"email": email, "password": password})
    return JSONResponse(content={"message": "Login endpoint — wire up Supabase here."})


@router.post("/logout")
async def logout():
    # TODO: supabase.auth.sign_out()
    return JSONResponse(content={"message": "Logged out."})
