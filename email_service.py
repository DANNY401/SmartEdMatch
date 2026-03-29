"""
SmartEdMatch — Email Confirmation Service using Resend
Uses 6-digit OTP codes instead of confirmation links.
This works regardless of where the app is hosted.

SETUP:
1. Go to resend.com → Sign up free
2. API Keys → Create API Key → copy it (starts with re_)
3. Replace YOUR_RESEND_API_KEY below with your real key

INSTALL:
pip install resend
"""

import secrets
import string
import random

# ── CONFIG ────────────────────────────────────────────────────────────────────
RESEND_API_KEY = "re_N25WSMJQ_HgS8zvhK94UiL5gBzDbQEeCc"   # replace with your key from resend.com
SENDER_EMAIL   = "onboarding@resend.dev" # use this for testing, or your own verified domain
SENDER_NAME    = "SmartEdMatch"


def generate_otp(length=6) -> str:
    """Generate a 6-digit OTP code."""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def generate_confirmation_token(length=32) -> str:
    """Generate a secure random token (kept for compatibility)."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_confirmation_email(to_email: str, student_name: str, token: str) -> dict:
    """
    Send a 6-digit OTP confirmation email to the student.
    The token parameter IS the 6-digit OTP code.

    Returns {"success": True, "otp": "123456"} or {"success": False, "error": "..."}
    """
    first_name = student_name.split()[0] if student_name else "Student"
    otp        = token  # token is now always a 6-digit OTP

    # Split OTP into individual digits for display
    digits = list(str(otp))

    html_body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#07101F;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr><td align="center" style="padding:40px 20px;">
<table width="560" cellpadding="0" cellspacing="0"
  style="background:#0B1A2E;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.08);">

  <!-- Header -->
  <tr>
    <td style="background:linear-gradient(135deg,#1D4ED8,#0891B2);padding:32px 40px;text-align:center;">
      <div style="font-size:32px;margin-bottom:8px;">🎓</div>
      <h1 style="color:#fff;font-size:24px;font-weight:800;margin:0 0 5px;">SmartEdMatch</h1>
      <p style="color:rgba(255,255,255,0.8);font-size:13px;margin:0;">Nigeria's AI Admission Intelligence System</p>
    </td>
  </tr>

  <!-- Body -->
  <tr>
    <td style="padding:36px 40px 28px;">
      <h2 style="color:#E2E8F0;font-size:20px;font-weight:700;margin:0 0 12px;">
        Hi {first_name}, here is your verification code 👋
      </h2>
      <p style="color:#94A3B8;font-size:14px;line-height:1.7;margin:0 0 28px;">
        Enter this 6-digit code in the SmartEdMatch app to confirm your email address
        and activate your account. The code expires in <strong style="color:#E2E8F0;">10 minutes</strong>.
      </p>

      <!-- OTP Code Box -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
        <tr>
          <td align="center">
            <div style="background:rgba(37,99,235,0.12);border:2px solid rgba(37,99,235,0.35);
            border-radius:14px;padding:20px 30px;display:inline-block;">
              <div style="font-size:11px;color:#64748B;font-weight:700;text-transform:uppercase;
              letter-spacing:0.1em;margin-bottom:10px;">Your Verification Code</div>
              <div style="display:flex;gap:8px;justify-content:center;">
                {''.join([f'<div style="width:42px;height:52px;background:#0D2040;border:1.5px solid rgba(37,99,235,0.4);border-radius:10px;display:inline-flex;align-items:center;justify-content:center;font-size:26px;font-weight:800;color:#60A5FA;font-family:monospace;">{d}</div>' for d in digits])}
              </div>
            </div>
          </td>
        </tr>
      </table>

      <!-- Instructions -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
        <tr>
          <td style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
          border-radius:12px;padding:16px 20px;">
            <p style="color:#94A3B8;font-size:13px;line-height:1.6;margin:0;">
              <strong style="color:#E2E8F0;">How to use this code:</strong><br>
              1. Go back to the SmartEdMatch app<br>
              2. Type this 6-digit code into the verification box<br>
              3. Click <strong style="color:#60A5FA;">Verify Code</strong> to activate your account
            </p>
          </td>
        </tr>
      </table>

      <p style="color:#334155;font-size:12px;text-align:center;margin:0;line-height:1.6;">
        This code expires in 10 minutes and can only be used once.<br>
        If you did not create a SmartEdMatch account, ignore this email.
      </p>
    </td>
  </tr>

  <!-- Feature strip -->
  <tr>
    <td style="padding:0 40px 28px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td width="32%" style="padding-right:6px;vertical-align:top;">
            <div style="background:rgba(37,99,235,0.08);border:1px solid rgba(37,99,235,0.18);
            border-radius:10px;padding:12px;text-align:center;">
              <div style="font-size:18px;margin-bottom:5px;">📐</div>
              <div style="color:#60A5FA;font-size:11px;font-weight:700;">JAMB Validator</div>
            </div>
          </td>
          <td width="32%" style="padding:0 3px;vertical-align:top;">
            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.18);
            border-radius:10px;padding:12px;text-align:center;">
              <div style="font-size:18px;margin-bottom:5px;">📊</div>
              <div style="color:#34D399;font-size:11px;font-weight:700;">Admission Probability</div>
            </div>
          </td>
          <td width="32%" style="padding-left:6px;vertical-align:top;">
            <div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.18);
            border-radius:10px;padding:12px;text-align:center;">
              <div style="font-size:18px;margin-bottom:5px;">🎯</div>
              <div style="color:#C4B5FD;font-size:11px;font-weight:700;">Safe / Ambitious</div>
            </div>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="background:#071018;padding:18px 40px;border-top:1px solid rgba(255,255,255,0.05);
    text-align:center;">
      <p style="color:#1E293B;font-size:11px;margin:0;line-height:1.7;">
        SmartEdMatch — AI-Driven Higher Institution Recommendation System for Nigeria<br>
        Aliyu Daniel Eshoraimeh · Veritas University, Abuja · 2025/2026
      </p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>
    """

    plain_text = (
        f"Hi {first_name},\n\n"
        f"Your SmartEdMatch verification code is: {otp}\n\n"
        f"Enter this code in the app to confirm your email.\n"
        f"This code expires in 10 minutes.\n\n"
        f"If you did not create a SmartEdMatch account, ignore this email.\n\n"
        f"SmartEdMatch — Nigeria's AI Admission Intelligence System"
    )

    # ── Demo mode ─────────────────────────────────────────────────────────────
    if RESEND_API_KEY == "YOUR_RESEND_API_KEY":
        print(f"\n{'='*55}")
        print("📧 DEMO MODE — Resend API key not set")
        print(f"   To   : {to_email}")
        print(f"   OTP  : {otp}  ← use this code to test")
        print(f"{'='*55}\n")
        return {"success": True, "demo": True, "otp": otp}

    # ── Production: send via Resend ───────────────────────────────────────────
    try:
        import resend
        resend.api_key = RESEND_API_KEY

        response = resend.Emails.send({
            "from": f"{SENDER_NAME} <{SENDER_EMAIL}>",
            "to":   [to_email],
            "subject": f"Your SmartEdMatch verification code: {otp}",
            "html": html_body,
            "text": plain_text,
        })

        if response and response.get("id"):
            return {"success": True, "demo": False, "id": response["id"], "otp": otp}
        else:
            return {"success": False, "error": "No email ID returned from Resend"}

    except ImportError:
        return {"success": False, "error": "Resend not installed. Run: pip install resend"}
    except Exception as e:
        err = str(e)
        if "401" in err or "API key" in err.lower():
            return {"success": False, "error": "Invalid Resend API key. Check resend.com/api-keys"}
        return {"success": False, "error": err}


def send_pro_upgrade_email(to_email: str, student_name: str) -> dict:
    """Send Pro upgrade confirmation email."""
    first_name = student_name.split()[0] if student_name else "Student"

    html_body = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#07101F;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr><td align="center" style="padding:40px 20px;">
<table width="560" cellpadding="0" cellspacing="0"
  style="background:#0B1A2E;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.08);">
  <tr>
    <td style="background:linear-gradient(135deg,#059669,#10B981);padding:32px 40px;text-align:center;">
      <div style="font-size:32px;margin-bottom:8px;">⭐</div>
      <h1 style="color:#fff;font-size:24px;font-weight:800;margin:0;">You're now SmartEdMatch Pro!</h1>
    </td>
  </tr>
  <tr>
    <td style="padding:36px 40px;">
      <p style="color:#94A3B8;font-size:15px;line-height:1.7;margin:0 0 20px;">
        Congratulations {first_name}! 🎉 Your Pro account is now active with
        unlimited searches, admission probability scores, campus sentiment analysis,
        and PDF report downloads.
      </p>
    </td>
  </tr>
  <tr>
    <td style="background:#071018;padding:18px 40px;border-top:1px solid rgba(255,255,255,0.05);text-align:center;">
      <p style="color:#1E293B;font-size:11px;margin:0;">SmartEdMatch · Veritas University, Abuja</p>
    </td>
  </tr>
</table>
</td></tr>
</table>
</body>
</html>
    """

    if RESEND_API_KEY == "YOUR_RESEND_API_KEY":
        print(f"📧 DEMO: Pro upgrade email → {to_email}")
        return {"success": True, "demo": True}
    try:
        import resend
        resend.api_key = RESEND_API_KEY
        r = resend.Emails.send({
            "from": f"{SENDER_NAME} <{SENDER_EMAIL}>",
            "to": [to_email],
            "subject": "⭐ Welcome to SmartEdMatch Pro!",
            "html": html_body,
        })
        return {"success": bool(r and r.get("id"))}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_password_reset_email(to_email: str, student_name: str, reset_token: str) -> dict:
    """Send password reset OTP email."""
    first_name = student_name.split()[0] if student_name else "Student"
    otp        = reset_token   # pass a 6-digit OTP as reset_token

    html_body = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#07101F;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr><td align="center" style="padding:40px 20px;">
<table width="560" cellpadding="0" cellspacing="0"
  style="background:#0B1A2E;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.08);">
  <tr>
    <td style="background:linear-gradient(135deg,#1D4ED8,#0891B2);padding:32px 40px;text-align:center;">
      <div style="font-size:32px;margin-bottom:8px;">🔐</div>
      <h1 style="color:#fff;font-size:24px;font-weight:800;margin:0;">Password Reset Code</h1>
    </td>
  </tr>
  <tr>
    <td style="padding:36px 40px;">
      <p style="color:#94A3B8;font-size:14px;line-height:1.7;margin:0 0 24px;">
        Hi {first_name}, use this code to reset your SmartEdMatch password. Expires in 10 minutes.
      </p>
      <div style="text-align:center;margin-bottom:24px;">
        <div style="background:rgba(37,99,235,0.12);border:2px solid rgba(37,99,235,0.35);
        border-radius:14px;padding:20px 30px;display:inline-block;">
          <div style="font-size:32px;font-weight:800;color:#60A5FA;font-family:monospace;
          letter-spacing:8px;">{otp}</div>
        </div>
      </div>
      <p style="color:#334155;font-size:12px;text-align:center;margin:0;">
        If you didn't request a password reset, ignore this email.
      </p>
    </td>
  </tr>
  <tr>
    <td style="background:#071018;padding:18px 40px;border-top:1px solid rgba(255,255,255,0.05);text-align:center;">
      <p style="color:#1E293B;font-size:11px;margin:0;">SmartEdMatch · Veritas University, Abuja</p>
    </td>
  </tr>
</table>
</td></tr>
</table>
</body>
</html>
    """

    if RESEND_API_KEY == "YOUR_RESEND_API_KEY":
        print(f"📧 DEMO: Password reset OTP {otp} → {to_email}")
        return {"success": True, "demo": True, "otp": otp}
    try:
        import resend
        resend.api_key = RESEND_API_KEY
        r = resend.Emails.send({
            "from": f"{SENDER_NAME} <{SENDER_EMAIL}>",
            "to": [to_email],
            "subject": f"Your SmartEdMatch password reset code: {otp}",
            "html": html_body,
        })
        return {"success": bool(r and r.get("id")), "otp": otp}
    except Exception as e:
        return {"success": False, "error": str(e)}
