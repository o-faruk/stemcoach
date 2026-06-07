from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import JSONResponse
import os
import stripe
from supabase import create_client

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PRICE_ID = os.getenv("STRIPE_PRICE_ID_BASIC")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)


@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    try:
        user = supabase.auth.get_user(token)
        email = user.user.email
        user_id = str(user.user.id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token.")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": PRICE_ID, "quantity": 1}],
            mode="subscription",
            customer_email=email,
            client_reference_id=user_id,
            success_url=f"{BASE_URL}/dashboard?subscribed=true",
            cancel_url=f"{BASE_URL}/dashboard?cancelled=true",
        )
        return JSONResponse(content={"checkout_url": session.url})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "customer.subscription.created":
        sub = event["data"]["object"]
        customer_id = sub["customer"]
        # Get customer email to find user
        customer = stripe.Customer.retrieve(customer_id)
        email = customer.get("email")
        if email:
            # Mark user as pro in Supabase
            users = supabase.auth.admin.list_users()
            for u in users:
                if u.email == email:
                    supabase.table("profiles").update({
                        "is_pro": True,
                        "stripe_customer_id": customer_id,
                        "stripe_subscription_id": sub["id"]
                    }).eq("id", str(u.id)).execute()
                    break

    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        customer_id = sub["customer"]
        supabase.table("profiles").update({
            "is_pro": False,
            "stripe_subscription_id": None
        }).eq("stripe_customer_id", customer_id).execute()

    return JSONResponse(content={"received": True})


@router.get("/status")
async def subscription_status(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    try:
        user = supabase.auth.get_user(token)
        user_id = str(user.user.id)
        result = supabase.table("profiles").select("is_pro").eq("id", user_id).execute()
        is_pro = result.data[0]["is_pro"] if result.data else False
        return JSONResponse(content={"is_pro": is_pro})
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token.")
