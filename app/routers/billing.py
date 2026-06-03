from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import os
import stripe

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PRICE_ID = os.getenv("STRIPE_PRICE_ID_BASIC")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@router.post("/create-checkout-session")
async def create_checkout_session(customer_email: str = Form(...)):
    """Create a Stripe Checkout session for the $9/month plan."""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": PRICE_ID, "quantity": 1}],
            mode="subscription",
            customer_email=customer_email,
            success_url=f"{BASE_URL}/dashboard?subscribed=true",
            cancel_url=f"{BASE_URL}/?cancelled=true",
        )
        return JSONResponse(content={"checkout_url": session.url})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks (subscription created, cancelled, etc.)"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "customer.subscription.created":
        # TODO: Mark user as subscribed in Supabase
        print(f"New subscription: {event['data']['object']}")

    elif event["type"] == "customer.subscription.deleted":
        # TODO: Revoke user access in Supabase
        print(f"Subscription cancelled: {event['data']['object']}")

    return JSONResponse(content={"received": True})
