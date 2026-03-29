"""
SmartEdMatch — Paystack Payment Integration
Handles Pro plan payments via Paystack (Nigeria's leading payment gateway)

SETUP:
1. Go to paystack.com → Sign up free
2. Dashboard → Settings → API Keys & Webhooks
3. Copy your Secret Key (starts with sk_test_ for testing, sk_live_ for production)
4. Replace YOUR_PAYSTACK_SECRET_KEY below
5. Set your callback URL to: https://yourapp.streamlit.app?payment=success

INSTALL:
pip install requests

FREE TO USE: Paystack charges 1.5% per transaction (capped at ₦2,000)
You keep 98.5% of every ₦2,500 Pro payment = ₦2,462.50 per subscriber
"""

import requests
import json
import hashlib
import hmac

# ── CONFIG ────────────────────────────────────────────────────────────────────
PAYSTACK_SECRET_KEY  = "YOUR_PAYSTACK_SECRET_KEY"  # from paystack.com dashboard
PAYSTACK_PUBLIC_KEY  = "YOUR_PAYSTACK_PUBLIC_KEY"  # from paystack.com dashboard
APP_CALLBACK_URL     = "https://smartedmatch.streamlit.app?payment=success"

PAYSTACK_BASE_URL    = "https://api.paystack.co"

# ── Pro plan pricing ──────────────────────────────────────────────────────────
PRO_MONTHLY_AMOUNT   = 250000   # ₦2,500 in kobo (Paystack uses kobo)
PRO_PLAN_NAME        = "SmartEdMatch Pro Monthly"
PRO_PLAN_INTERVAL    = "monthly"


# ── Initialize a payment transaction ─────────────────────────────────────────
def initialize_payment(email: str, student_name: str, amount_kobo: int = PRO_MONTHLY_AMOUNT) -> dict:
    """
    Initialize a Paystack payment transaction.
    Returns a payment URL that the student visits to pay.

    Returns:
        {"success": True, "payment_url": "...", "reference": "..."}
        {"success": False, "error": "..."}
    """
    if PAYSTACK_SECRET_KEY == "YOUR_PAYSTACK_SECRET_KEY":
        # Demo mode
        demo_ref = f"DEMO_REF_{email.split('@')[0].upper()}_PRO"
        return {
            "success": True,
            "demo": True,
            "payment_url": f"https://paystack.com/demo-pay/{demo_ref}",
            "reference": demo_ref,
            "message": "Demo mode — Paystack not configured yet"
        }

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": email,
        "amount": amount_kobo,
        "currency": "NGN",
        "callback_url": APP_CALLBACK_URL,
        "metadata": {
            "custom_fields": [
                {
                    "display_name": "Student Name",
                    "variable_name": "student_name",
                    "value": student_name
                },
                {
                    "display_name": "Plan",
                    "variable_name": "plan",
                    "value": "SmartEdMatch Pro Monthly"
                }
            ]
        }
    }

    try:
        response = requests.post(
            f"{PAYSTACK_BASE_URL}/transaction/initialize",
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )
        data = response.json()

        if data.get("status") and data.get("data"):
            return {
                "success": True,
                "demo": False,
                "payment_url": data["data"]["authorization_url"],
                "reference": data["data"]["reference"]
            }
        else:
            return {
                "success": False,
                "error": data.get("message", "Payment initialization failed")
            }
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Payment gateway timeout. Please try again."}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Verify a payment after callback ──────────────────────────────────────────
def verify_payment(reference: str) -> dict:
    """
    Verify that a payment was actually completed.
    Call this after the student returns from Paystack.

    Returns:
        {"success": True, "paid": True, "email": "...", "amount": ...}
        {"success": True, "paid": False}
        {"success": False, "error": "..."}
    """
    if PAYSTACK_SECRET_KEY == "YOUR_PAYSTACK_SECRET_KEY":
        # Demo mode — assume payment succeeded
        return {
            "success": True,
            "demo": True,
            "paid": True,
            "amount": PRO_MONTHLY_AMOUNT,
            "message": "Demo mode — payment assumed successful"
        }

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    }

    try:
        response = requests.get(
            f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}",
            headers=headers,
            timeout=10
        )
        data = response.json()

        if data.get("status") and data.get("data"):
            tx = data["data"]
            paid = tx.get("status") == "success"
            return {
                "success": True,
                "paid": paid,
                "email": tx.get("customer", {}).get("email", ""),
                "amount": tx.get("amount", 0),
                "reference": reference
            }
        else:
            return {"success": False, "error": data.get("message", "Verification failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Verify Paystack webhook signature ─────────────────────────────────────────
def verify_webhook(payload_bytes: bytes, signature: str) -> bool:
    """
    Verify that a webhook request actually came from Paystack.
    Use this in your webhook endpoint.
    """
    if PAYSTACK_SECRET_KEY == "YOUR_PAYSTACK_SECRET_KEY":
        return True  # Demo mode

    expected = hmac.new(
        PAYSTACK_SECRET_KEY.encode("utf-8"),
        payload_bytes,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


# ── Streamlit payment button ──────────────────────────────────────────────────
def render_payment_button(email: str, student_name: str) -> dict:
    """
    Renders a Paystack payment button using the JavaScript SDK inline.
    Call this from your Streamlit app to show a payment button.

    Usage in app.py:
        from payment_service import render_payment_button
        result = render_payment_button(user["email"], user["name"])
    """
    import streamlit as st

    if PAYSTACK_PUBLIC_KEY == "YOUR_PAYSTACK_PUBLIC_KEY":
        # Demo mode — show mock button
        st.markdown(f"""
        <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
        border-radius:12px;padding:1.2rem 1.5rem;text-align:center;">
            <div style="font-family:'Sora',sans-serif;font-size:0.9rem;font-weight:700;
            color:#34D399;margin-bottom:0.5rem;">💳 Pay ₦2,500/month via Paystack</div>
            <div style="font-size:0.78rem;color:#334155;">
                Paystack not configured yet. Add your API keys to payment_service.py
            </div>
        </div>
        """, unsafe_allow_html=True)
        return {"demo": True}

    # Production: inject Paystack inline JS
    paystack_html = f"""
    <script src="https://js.paystack.co/v1/inline.js"></script>
    <div style="text-align:center;margin:1rem 0;">
        <button onclick="payWithPaystack()" 
            style="background:linear-gradient(135deg,#059669,#10B981);color:#fff;
            border:none;border-radius:12px;padding:14px 40px;font-size:15px;
            font-weight:700;cursor:pointer;font-family:Sora,sans-serif;
            box-shadow:0 4px 18px rgba(16,185,129,0.35);">
            ⭐ Upgrade to Pro — ₦2,500/month
        </button>
    </div>
    <script>
    function payWithPaystack() {{
        var handler = PaystackPop.setup({{
            key: '{PAYSTACK_PUBLIC_KEY}',
            email: '{email}',
            amount: {PRO_MONTHLY_AMOUNT},
            currency: 'NGN',
            ref: 'SMEDPRO_' + Math.floor(Math.random() * 1000000000),
            metadata: {{
                custom_fields: [
                    {{ display_name: 'Student', variable_name: 'name', value: '{student_name}' }},
                    {{ display_name: 'Plan', variable_name: 'plan', value: 'Pro Monthly' }}
                ]
            }},
            callback: function(response) {{
                window.location.href = window.location.href + '&payment_ref=' + response.reference;
            }},
            onClose: function() {{
                alert('Payment window closed. Your account has not been upgraded yet.');
            }}
        }});
        handler.openIframe();
    }}
    </script>
    """
    st.components.v1.html(paystack_html, height=100)
    return {"demo": False}


# ── Format amount ─────────────────────────────────────────────────────────────
def format_naira(kobo_amount: int) -> str:
    """Convert kobo to formatted Naira string."""
    naira = kobo_amount / 100
    return f"₦{naira:,.0f}"
