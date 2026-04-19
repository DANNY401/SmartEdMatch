"""
SmartEdMatch — Email Service
Primary:  Gmail SMTP  (sends to ANY email — free, no domain needed)
Fallback: Resend API  (if RESEND_API_KEY is set in Streamlit secrets)

─── SETUP (Gmail SMTP — recommended) ────────────────────────────────────────
1. Go to myaccount.google.com → Security → 2-Step Verification → turn ON
2. Search "App passwords" → create one → name it "SmartEdMatch"
3. Copy the 16-char password (e.g. abcd efgh ijkl mnop)
4. In Streamlit Cloud → App Settings → Secrets, add:

   GMAIL_SENDER   = "yourgmail@gmail.com"
   GMAIL_PASSWORD = "abcdefghijklmnop"       ← no spaces

─── SETUP (Resend fallback — optional) ──────────────────────────────────────
1. resend.com → sign up → API Keys → create key
2. Domains → add and verify your domain (required to send to anyone)
3. Add to Streamlit secrets:
   RESEND_API_KEY    = "re_xxxxxxxxxxxx"
   RESEND_FROM_EMAIL = "noreply@yourdomain.com"
"""

import secrets
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Config — loaded from Streamlit secrets ────────────────────────────────────
try:
    import streamlit as st
    _s = st.secrets
    GMAIL_SENDER    = _s.get("GMAIL_SENDER",    "")
    GMAIL_PASSWORD  = _s.get("GMAIL_PASSWORD",  "")
    RESEND_API_KEY  = _s.get("RESEND_API_KEY",  "")
    RESEND_FROM     = _s.get("RESEND_FROM_EMAIL", "")
except Exception:
    GMAIL_SENDER   = ""
    GMAIL_PASSWORD = ""
    RESEND_API_KEY = ""
    RESEND_FROM    = ""

SENDER_NAME = "SmartEdMatch"


# ── OTP generation (cryptographically secure) ─────────────────────────────────
def generate_otp(length: int = 6) -> str:
    """Generate a cryptographically secure N-digit OTP using secrets module."""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


# ── HTML email builder ────────────────────────────────────────────────────────
def _build_otp_html(first_name: str, otp: str) -> str:
    digits = list(str(otp))
    digit_boxes = "".join([
        f'<div style="width:42px;height:52px;background:#0D2040;border:1.5px solid '
        f'rgba(37,99,235,0.4);border-radius:10px;display:inline-flex;align-items:center;'
        f'justify-content:center;font-size:26px;font-weight:800;color:#60A5FA;'
        f'font-family:monospace;margin:0 3px;">{d}</div>'
        for d in digits
    ])
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#07101F;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr><td align="center" style="padding:40px 20px;">
<table width="560" cellpadding="0" cellspacing="0"
  style="background:#0B1A2E;border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.08);">
  <tr>
    <td style="background:linear-gradient(135deg,#1D4ED8,#0891B2);padding:32px 40px;text-align:center;">
      <div style="font-size:32px;margin-bottom:8px;">🎓</div>
      <h1 style="color:#fff;font-size:24px;font-weight:800;margin:0 0 5px;">SmartEdMatch</h1>
      <p style="color:rgba(255,255,255,0.8);font-size:13px;margin:0;">Nigeria's AI Admission Intelligence System</p>
    </td>
  </tr>
  <tr>
    <td style="padding:36px 40px 28px;">
      <h2 style="color:#E2E8F0;font-size:20px;font-weight:700;margin:0 0 12px;">
        Hi {first_name}, here is your verification code 👋
      </h2>
      <p style="color:#94A3B8;font-size:14px;line-height:1.7;margin:0 0 28px;">
        Enter this 6-digit code in the SmartEdMatch app to confirm your email address
        and activate your account. The code expires in <strong style="color:#E2E8F0;">10 minutes</strong>.
      </p>
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
        <tr><td align="center">
          <div style="background:rgba(37,99,235,0.12);border:2px solid rgba(37,99,235,0.35);
          border-radius:14px;padding:20px 30px;display:inline-block;">
            <div style="font-size:11px;color:#64748B;font-weight:700;text-transform:uppercase;
            letter-spacing:0.1em;margin-bottom:10px;">Your Verification Code</div>
            <div style="display:flex;gap:8px;justify-content:center;">{digit_boxes}</div>
          </div>
        </td></tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
        <tr><td style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
        border-radius:12px;padding:16px 20px;">
          <p style="color:#94A3B8;font-size:13px;line-height:1.6;margin:0;">
            <strong style="color:#E2E8F0;">How to use this code:</strong><br>
            1. Go back to the SmartEdMatch app<br>
            2. Type this 6-digit code into the verification box<br>
            3. Click <strong style="color:#60A5FA;">Verify Code</strong> to activate your account
          </p>
        </td></tr>
      </table>
      <p style="color:#334155;font-size:12px;text-align:center;margin:0;line-height:1.6;">
        This code expires in 10 minutes and can only be used once.<br>
        If you did not create a SmartEdMatch account, ignore this email.
      </p>
    </td>
  </tr>
  <tr>
    <td style="padding:0 40px 28px;">
      <table width="100%" cellpadding="0" cellspacing="0"><tr>
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
      </tr></table>
    </td>
  </tr>
  <tr>
    <td style="background:#071018;padding:18px 40px;border-top:1px solid rgba(255,255,255,0.05);text-align:center;">
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
</html>"""


def _build_otp_plain(first_name: str, otp: str) -> str:
    return (
        f"Hi {first_name},\n\n"
        f"Your SmartEdMatch verification code is: {otp}\n\n"
        f"Enter this code in the app to confirm your email.\n"
        f"This code expires in 10 minutes.\n\n"
        f"If you did not create a SmartEdMatch account, ignore this email.\n\n"
        f"SmartEdMatch — Nigeria's AI Admission Intelligence System"
    )


# ── Gmail SMTP sender ─────────────────────────────────────────────────────────
def _send_via_gmail(to_email: str, subject: str, html: str, plain: str) -> dict:
    """
    Send email via Gmail SMTP with TLS.
    Works with any recipient email address globally.
    Requires GMAIL_SENDER and GMAIL_PASSWORD (App Password) in Streamlit secrets.
    """
    if not GMAIL_SENDER or not GMAIL_PASSWORD:
        return {"success": False, "error": "Gmail not configured — set GMAIL_SENDER and GMAIL_PASSWORD in Streamlit secrets"}

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{SENDER_NAME} <{GMAIL_SENDER}>"
    msg["To"]      = to_email

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html,  "html"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
        server.login(GMAIL_SENDER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_SENDER, to_email, msg.as_string())

    return {"success": True, "method": "gmail"}


# ── Resend sender ─────────────────────────────────────────────────────────────
def _send_via_resend(to_email: str, subject: str, html: str, plain: str) -> dict:
    """
    Send via Resend API.
    Requires RESEND_API_KEY and RESEND_FROM_EMAIL (verified domain sender) in secrets.
    NOTE: onboarding@resend.dev only works for the Resend account owner's email.
    You MUST verify a domain in Resend and set RESEND_FROM_EMAIL to use it.
    """
    if not RESEND_API_KEY or not RESEND_FROM:
        return {"success": False, "error": "Resend not configured"}
    try:
        import resend
        resend.api_key = RESEND_API_KEY
        response = resend.Emails.send({
            "from":    f"{SENDER_NAME} <{RESEND_FROM}>",
            "to":      [to_email],
            "subject": subject,
            "html":    html,
            "text":    plain,
        })
        if response and response.get("id"):
            return {"success": True, "method": "resend", "id": response["id"]}
        return {"success": False, "error": "No email ID returned from Resend"}
    except ImportError:
        return {"success": False, "error": "resend package not installed"}
    except Exception as e:
        err = str(e)
        if "401" in err or "api key" in err.lower():
            return {"success": False, "error": "Invalid Resend API key"}
        if "422" in err or "domain" in err.lower():
            return {"success": False, "error": "Resend sender domain not verified — add RESEND_FROM_EMAIL to secrets"}
        return {"success": False, "error": err}


# ── Demo mode (terminal output) ───────────────────────────────────────────────
def _demo_mode(to_email: str, otp: str) -> dict:
    print(f"\n{'='*55}")
    print("📧 DEMO MODE — email credentials not configured")
    print(f"   To   : {to_email}")
    print(f"   OTP  : {otp}  ← use this code to test")
    print(f"{'='*55}\n")
    return {"success": True, "demo": True, "otp": otp}


# ── Public API ────────────────────────────────────────────────────────────────
def send_confirmation_email(to_email: str, student_name: str, token: str) -> dict:
    """
    Send OTP verification email. Tries Gmail first, then Resend, then demo mode.
    token = 6-digit OTP string.
    """
    first_name = student_name.split()[0] if student_name else "Student"
    otp        = token
    subject    = f"Your SmartEdMatch verification code: {otp}"
    html       = _build_otp_html(first_name, otp)
    plain      = _build_otp_plain(first_name, otp)

    # 1. Try Gmail SMTP (primary — works with any email address)
    if GMAIL_SENDER and GMAIL_PASSWORD:
        try:
            result = _send_via_gmail(to_email, subject, html, plain)
            if result["success"]:
                return {**result, "otp": otp}
        except Exception as e:
            pass  # fall through to Resend

    # 2. Try Resend (secondary — requires verified domain)
    if RESEND_API_KEY and RESEND_FROM:
        try:
            result = _send_via_resend(to_email, subject, html, plain)
            if result["success"]:
                return {**result, "otp": otp}
        except Exception:
            pass

    # 3. Demo mode (prints OTP to terminal/logs)
    return _demo_mode(to_email, otp)


def send_pro_upgrade_email(to_email: str, student_name: str) -> dict:
    """Send Pro upgrade confirmation email."""
    first_name = student_name.split()[0] if student_name else "Student"
    subject    = "⭐ Welcome to SmartEdMatch Pro!"
    html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#07101F;font-family:'Segoe UI',Arial,sans-serif;">
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
</body></html>"""
    plain = f"Congratulations {first_name}! Your SmartEdMatch Pro account is now active."

    if GMAIL_SENDER and GMAIL_PASSWORD:
        try:
            return _send_via_gmail(to_email, subject, html, plain)
        except Exception:
            pass
    if RESEND_API_KEY and RESEND_FROM:
        try:
            return _send_via_resend(to_email, subject, html, plain)
        except Exception:
            pass
    print(f"📧 DEMO: Pro upgrade email → {to_email}")
    return {"success": True, "demo": True}


def send_password_reset_email(to_email: str, student_name: str, reset_token: str) -> dict:
    """Send password reset OTP email."""
    first_name = student_name.split()[0] if student_name else "Student"
    otp        = reset_token
    subject    = f"Your SmartEdMatch password reset code: {otp}"
    html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#07101F;font-family:'Segoe UI',Arial,sans-serif;">
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
</body></html>"""
    plain = f"Hi {first_name}, your SmartEdMatch password reset code is: {otp}\nExpires in 10 minutes."

    if GMAIL_SENDER and GMAIL_PASSWORD:
        try:
            result = _send_via_gmail(to_email, subject, html, plain)
            if result["success"]:
                return {**result, "otp": otp}
        except Exception:
            pass
    if RESEND_API_KEY and RESEND_FROM:
        try:
            result = _send_via_resend(to_email, subject, html, plain)
            if result["success"]:
                return {**result, "otp": otp}
        except Exception:
            pass
    print(f"📧 DEMO: Password reset OTP {otp} → {to_email}")
    return {"success": True, "demo": True, "otp": otp}


# ── Legacy alias kept for backward compatibility ──────────────────────────────
def generate_confirmation_token(length: int = 32) -> str:
    """Generate a secure random token. Kept for backward compatibility."""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))
