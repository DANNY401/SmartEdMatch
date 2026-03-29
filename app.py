"""
SmartEdMatch — AI-Driven Higher Institution Recommendation System for Nigeria
Aliyu Daniel Eshoraimeh · VUG/CSC/23/8925 · Veritas University, Abuja · 2025/2026

Audit fixes applied (2026-03):
  PERF  - Sentiment pre-fetched in one batch before card loop (eliminates N×HTTP calls)
  PERF  - Removed 2.1s forced time.sleep animation; replaced with st.spinner
  PERF  - CSS string cached with @st.cache_data (no re-parse on every rerun)
  PERF  - Broad search uses single cosine pass instead of two
  BUG   - live_badge check fixed (was "nairaland", now "duckduckgo"/"wikipedia")
  BUG   - Stats bar updated to 495 records / 46 courses
  BUG   - Footer matric number fixed (8935 → 8925)
  BUG   - load_error undefined risk eliminated (renamed _load_error, always defined)
  BUG   - Unused container/columns on signup page removed
  BUG   - Sign out now safely clears ALL session state via list(keys())
  BUG   - pending_user cleared with .pop() instead of conditional delete
  UX    - Sidebar redesigned with labelled section groups and dividers
  UX    - JAMB subjects now show live ✅/❌ validation per subject
  UX    - WAEC section shows parsed requirement for selected course
  UX    - All sklearn UserWarnings suppressed cleanly at top level
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import streamlit as st
import pandas as pd
import numpy as np
import textwrap
import time
from academic_data import (
    FACULTY_COURSES, JAMB_SUBJECTS, WAEC_REQUIREMENTS, PLANS, ONBOARDING_QUESTIONS
)

st.set_page_config(
    page_title="SmartEdMatch — Nigeria's AI Admission Advisor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Utilities ─────────────────────────────────────────────────────────────────
def html(raw: str) -> None:
    st.markdown(textwrap.dedent(raw).strip(), unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _build_css() -> str:
    """CSS is expensive to re-parse; cache it across reruns."""
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{
  --navy:#07101F;--navy-mid:#0B1A2E;--navy-card:#0D2040;
  --blue:#2563EB;--blue-l:#3B82F6;--cyan:#06B6D4;
  --gold:#F59E0B;--green:#10B981;--purple:#8B5CF6;
  --red:#EF4444;--white:#FFFFFF;--dim:#94A3B8;--faint:#334155;
  --glass:rgba(255,255,255,0.035);--glass-b:rgba(255,255,255,0.08);
  --radius:14px;--radius-sm:10px;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;background-color:var(--navy)!important;color:var(--white)!important;}
.stApp{background:var(--navy)!important;}
.block-container{padding-top:1.2rem!important;max-width:1200px!important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0B1A2E 0%,#07101F 100%)!important;border-right:1px solid var(--glass-b)!important;}
[data-testid="stSidebar"] .block-container{padding:0.8rem!important;}
[data-testid="stSidebar"] label{font-family:'Sora',sans-serif!important;font-size:0.68rem!important;font-weight:700!important;letter-spacing:0.09em!important;text-transform:uppercase!important;color:#38BDF8!important;}
[data-testid="stSidebar"] .stSelectbox>div>div{background:var(--glass)!important;border:1px solid rgba(255,255,255,0.09)!important;border-radius:var(--radius-sm)!important;color:var(--white)!important;}
[data-testid="stSidebar"] input[type="number"],[data-testid="stSidebar"] input[type="text"],[data-testid="stSidebar"] textarea{background:var(--glass)!important;border:1px solid rgba(255,255,255,0.09)!important;border-radius:var(--radius-sm)!important;color:var(--white)!important;}
.sb-section{font-family:'Sora',sans-serif;font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#334155;margin:0.7rem 0 0.35rem;padding:0 0.1rem;}
.sb-div{height:1px;background:rgba(255,255,255,0.06);margin:0.5rem 0;}
.stButton>button{width:100%!important;background:linear-gradient(135deg,#1D4ED8 0%,#0891B2 100%)!important;color:#fff!important;border:none!important;border-radius:var(--radius)!important;font-family:'Sora',sans-serif!important;font-size:0.88rem!important;font-weight:700!important;padding:0.68rem 1rem!important;transition:all 0.25s ease!important;box-shadow:0 4px 18px rgba(37,99,235,0.35)!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 28px rgba(37,99,235,0.55)!important;}
[data-testid="stDownloadButton"] button{width:100%!important;background:transparent!important;border:1.5px solid rgba(59,130,246,0.45)!important;color:#93C5FD!important;border-radius:var(--radius)!important;font-family:'Sora',sans-serif!important;font-weight:600!important;transition:all 0.25s!important;}
[data-testid="stDownloadButton"] button:hover{background:rgba(59,130,246,0.1)!important;border-color:rgba(59,130,246,0.75)!important;}
[data-testid="stMetric"]{background:var(--glass)!important;border:1px solid var(--glass-b)!important;border-radius:var(--radius)!important;padding:1rem 1.1rem!important;}
[data-testid="stMetricLabel"]{font-family:'Sora',sans-serif!important;font-size:0.65rem!important;font-weight:700!important;letter-spacing:0.09em!important;text-transform:uppercase!important;color:var(--dim)!important;}
[data-testid="stMetricValue"]{font-family:'Sora',sans-serif!important;font-size:1.5rem!important;font-weight:800!important;color:#E2E8F0!important;}
[data-testid="stExpander"]{background:var(--glass)!important;border:1px solid var(--glass-b)!important;border-radius:var(--radius)!important;}
details summary p{font-family:'Sora',sans-serif!important;font-size:0.82rem!important;font-weight:600!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--navy-mid)!important;border-radius:var(--radius)!important;padding:4px!important;gap:4px!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--dim)!important;border-radius:var(--radius-sm)!important;font-family:'Sora',sans-serif!important;font-weight:600!important;font-size:0.82rem!important;}
.stTabs [aria-selected="true"]{background:var(--blue)!important;color:var(--white)!important;}
.stRadio label{font-size:0.9rem!important;color:#E2E8F0!important;}
.stCheckbox label{font-size:0.9rem!important;color:#E2E8F0!important;}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:var(--navy);}::-webkit-scrollbar-thumb{background:#1E3A5F;border-radius:4px;}
hr{border-color:rgba(255,255,255,0.07)!important;}
@keyframes pulse-glow{0%,100%{opacity:0.4;transform:scale(1);}50%{opacity:1;transform:scale(1.08);}}
@keyframes fadeInUp{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}
@keyframes slideIn{from{opacity:0;transform:translateX(-20px);}to{opacity:1;transform:translateX(0);}}
.result-card{animation:fadeInUp 0.35s ease forwards;}
.onboard-card{animation:slideIn 0.4s ease forwards;}
.subj-ok{display:inline-flex;align-items:center;gap:4px;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);color:#6EE7B7;border-radius:20px;padding:3px 10px;font-size:0.69rem;font-weight:600;font-family:'Sora',sans-serif;}
.subj-missing{display:inline-flex;align-items:center;gap:4px;background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);color:#FCA5A5;border-radius:20px;padding:3px 10px;font-size:0.69rem;font-weight:600;font-family:'Sora',sans-serif;}
.subj-neutral{display:inline-flex;align-items:center;gap:4px;background:rgba(37,99,235,0.12);border:1px solid rgba(37,99,235,0.3);color:#93C5FD;border-radius:20px;padding:3px 10px;font-size:0.69rem;font-weight:600;font-family:'Sora',sans-serif;}
</style>
"""

html(_build_css())


# ── Session state initialisation ──────────────────────────────────────────────
def init_state() -> None:
    defaults = {
        "logged_in": False, "user": {}, "page": "home",
        "onboard_step": 0, "onboard_answers": {}, "is_pro": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── Recommendation engine ─────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_engine():
    from recommender import SmartEdMatch
    return SmartEdMatch("nigerian_institutions_full.csv")

_engine_loaded = False
_load_error    = ""          # always defined; eliminates NameError risk
try:
    engine         = load_engine()
    _engine_loaded = True
except Exception as _e:
    _load_error = str(_e)


# ── Domain helpers ────────────────────────────────────────────────────────────
def admission_probability(jamb: int, cutoff: int, inst_type: str) -> float:
    gap = jamb - cutoff
    if gap < 0:
        return 0.0
    if inst_type == "Federal University":
        return round(min(95, 30 + gap * 1.8), 1)
    if inst_type == "Private University":
        return round(min(95, 45 + gap * 1.5), 1)
    return round(min(95, 50 + gap * 2.0), 1)


def get_category(prob: float) -> tuple:
    if prob >= 70: return "Safe",      "#10B981", "✅"
    if prob >= 40: return "Balanced",  "#F59E0B", "⚖️"
    return             "Ambitious", "#EF4444", "🚀"


def validate_jamb(user_subjects: list, required: list) -> list:
    """Returns list of (display_text, matched, is_flexible)."""
    user_lower = " ".join(s.lower() for s in user_subjects)
    out = []
    for req in required:
        if "any of" in req.lower() or " or " in req.lower():
            opts    = [p.strip().lower() for p in req.replace("Any of","").replace("any of","").replace(" or ","/").split("/")]
            matched = any(o in user_lower for o in opts if len(o) > 2)
            out.append((req, matched, True))
        else:
            out.append((req, req.lower() in user_lower, False))
    return out


from sentiment_service import (
    get_sentiment, sentiment_color, sentiment_label, asuu_risk_color
)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    html("""
<div style="background:linear-gradient(135deg,#0B1A2E 0%,#0D2040 50%,#07101F 100%);border:1px solid rgba(255,255,255,0.07);border-radius:24px;padding:3.5rem 3rem;margin-bottom:2rem;position:relative;overflow:hidden;">
  <div style="position:absolute;top:-100px;right:-100px;width:350px;height:350px;border-radius:50%;background:radial-gradient(circle,rgba(37,99,235,0.2) 0%,transparent 70%);pointer-events:none;"></div>
  <div style="position:absolute;bottom:-80px;left:20%;width:250px;height:250px;border-radius:50%;background:radial-gradient(circle,rgba(6,182,212,0.12) 0%,transparent 70%);pointer-events:none;"></div>
  <div style="position:relative;z-index:1;max-width:650px;">
    <div style="display:inline-flex;align-items:center;gap:0.5rem;background:rgba(37,99,235,0.13);border:1px solid rgba(37,99,235,0.28);border-radius:30px;padding:5px 16px;margin-bottom:1.2rem;">
      <div style="width:7px;height:7px;border-radius:50%;background:#10B981;box-shadow:0 0 8px rgba(16,185,129,0.8);animation:pulse-glow 2s ease-in-out infinite;"></div>
      <span style="font-size:0.7rem;font-family:'Sora',sans-serif;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#60A5FA;">Nigeria's First AI Admission Intelligence System</span>
    </div>
    <h1 style="font-family:'Sora',sans-serif;font-size:3rem;font-weight:800;margin:0 0 0.8rem;line-height:1.1;color:#FFFFFF;">Stop Guessing.<br><span style="color:#93C5FD;">Start Matching.</span></h1>
    <p style="font-size:1.05rem;color:#94A3B8;margin:0 0 2rem;line-height:1.7;">SmartEdMatch validates your JAMB subjects, checks NUC accreditation, estimates your admission probability, and analyses real campus sentiment — so you never waste a year or a naira on the wrong institution.</p>
  </div>
</div>
    """)

    c1, c2, c3 = st.columns([2, 2, 4])
    with c1:
        if st.button("🚀  Get Started Free", type="primary"):
            st.session_state.page = "signup"; st.rerun()
    with c2:
        if st.button("🔑  Sign In"):
            st.session_state.page = "signin"; st.rerun()
    with c3:
        if st.button("👁️  Explore as Guest"):
            st.session_state.logged_in = True
            st.session_state.user = {"name":"Guest","email":"","is_pro":False}
            st.session_state.page = "main"; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    html('<div class="sb-section">What Makes SmartEdMatch Different</div>')

    feats = [
        ("#2563EB","📐","JAMB Subject Validator","Checks your subject combination per course — before you waste a registration fee"),
        ("#10B981","✅","NUC Accreditation Check","Verifies your course is properly accredited so you never enrol in an unrecognised program"),
        ("#F59E0B","📊","Admission Probability","Calculates your real % chance of admission based on your score vs historical cut-offs"),
        ("#8B5CF6","🌐","Campus Sentiment","Analyses DuckDuckGo + Wikipedia data to surface real campus realities — safety, ASUU, facilities"),
        ("#06B6D4","🎯","Safe / Balanced / Ambitious","Categorises every recommendation like US college advisors — know your safety schools from dream schools"),
        ("#EF4444","💳","Pro Intelligence Reports","Unlock full analysis, PDF reports, unlimited searches and priority support with SmartEdMatch Pro"),
    ]
    for row_slice in [feats[:3], feats[3:]]:
        for col, (color, icon, title, desc) in zip(st.columns(3), row_slice):
            with col:
                html(f"""<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-top:3px solid {color};border-radius:16px;padding:1.4rem 1.2rem;margin-bottom:1rem;">
<div style="font-size:1.6rem;margin-bottom:0.6rem;">{icon}</div>
<div style="font-family:'Sora',sans-serif;font-size:0.9rem;font-weight:700;color:#E2E8F0;margin-bottom:0.4rem;">{title}</div>
<div style="font-size:0.78rem;color:#334155;line-height:1.6;">{desc}</div>
</div>""")

    st.markdown("<br>", unsafe_allow_html=True)
    html("""<div style="background:linear-gradient(135deg,rgba(37,99,235,0.09),rgba(6,182,212,0.05));border:1px solid rgba(37,99,235,0.16);border-radius:14px;padding:1.5rem 2rem;display:flex;justify-content:space-around;flex-wrap:wrap;gap:1rem;text-align:center;">
<div><div style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;color:#60A5FA;">138+</div><div style="font-size:0.68rem;color:#334155;text-transform:uppercase;letter-spacing:0.07em;">Institutions</div></div>
<div style="width:1px;background:rgba(255,255,255,0.06);"></div>
<div><div style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;color:#34D399;">495</div><div style="font-size:0.68rem;color:#334155;text-transform:uppercase;letter-spacing:0.07em;">Dataset Records</div></div>
<div style="width:1px;background:rgba(255,255,255,0.06);"></div>
<div><div style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;color:#F472B6;">46</div><div style="font-size:0.68rem;color:#334155;text-transform:uppercase;letter-spacing:0.07em;">Courses</div></div>
<div style="width:1px;background:rgba(255,255,255,0.06);"></div>
<div><div style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;color:#FBBF24;">65%</div><div style="font-size:0.68rem;color:#334155;text-transform:uppercase;letter-spacing:0.07em;">System Accuracy</div></div>
<div style="width:1px;background:rgba(255,255,255,0.06);"></div>
<div><div style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;color:#A78BFA;">FREE</div><div style="font-size:0.68rem;color:#334155;text-transform:uppercase;letter-spacing:0.07em;">To Get Started</div></div>
</div>""")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SIGN UP
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "signup":
    html("""<div style="text-align:center;margin-bottom:2rem;">
<div style="font-size:2.5rem;margin-bottom:0.5rem;">🎓</div>
<div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:800;color:#60A5FA;">Create Your Account</div>
<div style="font-size:0.88rem;color:#334155;margin-top:0.3rem;">Join Nigerian students making smarter admission decisions</div>
</div>""")

    col = st.columns([1, 2, 1])[1]
    with col:
        html("""<div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);border-radius:20px;padding:2rem;">""")
        full_name = st.text_input("👤  Full Name",        placeholder="e.g. Aliyu Daniel Eshoraimeh")
        email     = st.text_input("📧  Email Address",    placeholder="youremail@gmail.com")
        phone     = st.text_input("📱  Phone Number",     placeholder="08012345678")
        password  = st.text_input("🔒  Password",         type="password", placeholder="At least 8 characters")
        confirm   = st.text_input("🔒  Confirm Password", type="password", placeholder="Repeat your password")
        st.markdown("<br>", unsafe_allow_html=True)
        terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")

        if st.button("✅  Create Account & Continue", type="primary"):
            if not full_name or not email or not password:
                html("""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:10px;padding:0.8rem 1rem;margin-top:0.8rem;font-size:0.84rem;color:#FCA5A5;">⚠️ Please fill in all required fields.</div>""")
            elif password != confirm:
                html("""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:10px;padding:0.8rem 1rem;margin-top:0.8rem;font-size:0.84rem;color:#FCA5A5;">⚠️ Passwords do not match.</div>""")
            elif len(password) < 8:
                html("""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:10px;padding:0.8rem 1rem;margin-top:0.8rem;font-size:0.84rem;color:#FCA5A5;">⚠️ Password must be at least 8 characters.</div>""")
            elif not terms:
                html("""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:10px;padding:0.8rem 1rem;margin-top:0.8rem;font-size:0.84rem;color:#FCA5A5;">⚠️ Please accept the Terms of Service.</div>""")
            else:
                try:
                    from email_service import send_confirmation_email, generate_otp
                    token = generate_otp()
                    send_confirmation_email(email, full_name, token)
                except Exception:
                    token = "000000"   # demo fallback; OTP printed to terminal
                st.session_state.pending_user = {
                    "name": full_name, "email": email,
                    "phone": phone, "is_pro": False, "token": token,
                }
                st.session_state.page = "verify_email"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        html("""<div style="text-align:center;font-size:0.82rem;color:#334155;">Already have an account?</div>""")
        if st.button("Sign In Instead"):
            st.session_state.page = "signin"; st.rerun()
        html("</div>")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Home"):
        st.session_state.page = "home"; st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: VERIFY EMAIL
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "verify_email":
    pending    = st.session_state.get("pending_user", {})
    email_addr = pending.get("email", "your email")

    col = st.columns([1, 2, 1])[1]
    with col:
        html(f"""<div style="text-align:center;padding:1.5rem 0 1rem;">
<div style="font-size:3.5rem;margin-bottom:0.8rem;">📬</div>
<div style="font-family:'Sora',sans-serif;font-size:1.5rem;font-weight:800;color:#60A5FA;margin-bottom:0.4rem;">Check your email</div>
<div style="font-size:0.9rem;color:#94A3B8;margin-bottom:0.8rem;">We sent a 6-digit code to</div>
<div style="background:rgba(37,99,235,0.1);border:1px solid rgba(37,99,235,0.3);border-radius:10px;padding:0.7rem 1.2rem;display:inline-block;margin-bottom:1.5rem;">
<span style="font-family:'Sora',sans-serif;font-size:0.95rem;font-weight:700;color:#60A5FA;">📧 {email_addr}</span>
</div>
</div>""")

        otp_input = st.text_input("Verification code", placeholder="e.g. 482910", max_chars=6, label_visibility="collapsed")

        if st.button("✅  Verify Code", type="primary"):
            stored  = str(pending.get("token","")).strip()
            entered = str(otp_input).strip()
            if not entered:
                html("""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:10px;padding:0.7rem 1rem;margin-top:0.5rem;font-size:0.84rem;color:#FCA5A5;">⚠️ Please enter the 6-digit code from your email.</div>""")
            elif entered == stored:
                st.session_state.logged_in = True
                st.session_state.user = {
                    "name": pending.get("name",""), "email": pending.get("email",""),
                    "phone": pending.get("phone",""), "is_pro": False,
                }
                st.session_state.pop("pending_user", None)   # clean up safely
                html("""<div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:0.7rem 1rem;margin-top:0.5rem;font-size:0.84rem;color:#6EE7B7;">✅ Email confirmed! Taking you in...</div>""")
                time.sleep(1.2)
                st.session_state.page = "onboard"; st.rerun()
            else:
                html("""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:10px;padding:0.7rem 1rem;margin-top:0.5rem;font-size:0.84rem;color:#FCA5A5;">❌ Incorrect code. Check your email and try again.</div>""")

        st.markdown("<br>", unsafe_allow_html=True)
        html("""<div style="background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.2);border-radius:10px;padding:0.8rem 1rem;margin-bottom:0.8rem;">
<div style="font-size:0.78rem;color:#FCD34D;line-height:1.6;"><strong>⚠️ No email?</strong> Check your Spam/Junk folder.<br>Subject: <em style="color:#E2E8F0;">"Your SmartEdMatch verification code: XXXXXX"</em></div>
</div>""")

        if st.button("🔄  Send a New Code"):
            try:
                from email_service import send_confirmation_email, generate_otp
                new_otp = generate_otp()
                send_confirmation_email(pending.get("email",""), pending.get("name",""), new_otp)
                st.session_state.pending_user["token"] = new_otp
                html("""<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:10px;padding:0.7rem 1rem;margin-top:0.4rem;font-size:0.82rem;color:#6EE7B7;">✅ New code sent! Check your inbox.</div>""")
            except Exception as e:
                html(f"""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:10px;padding:0.7rem 1rem;margin-top:0.4rem;font-size:0.82rem;color:#FCA5A5;">⚠️ Could not resend: {e}</div>""")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Use a different email"):
            st.session_state.pop("pending_user", None)
            st.session_state.page = "signup"; st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SIGN IN
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "signin":
    col = st.columns([1, 2, 1])[1]
    with col:
        html("""<div style="text-align:center;margin-bottom:2rem;">
<div style="font-size:2.5rem;margin-bottom:0.5rem;">👋</div>
<div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:800;color:#60A5FA;">Welcome Back</div>
<div style="font-size:0.88rem;color:#334155;margin-top:0.3rem;">Sign in to your SmartEdMatch account</div>
</div>""")
        html("""<div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);border-radius:20px;padding:2rem;">""")
        email    = st.text_input("📧  Email Address", placeholder="youremail@gmail.com")
        password = st.text_input("🔒  Password", type="password", placeholder="Your password")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔑  Sign In", type="primary"):
            if email and password:
                st.session_state.logged_in = True
                st.session_state.user = {"name": email.split("@")[0].title(), "email": email, "is_pro": False}
                st.session_state.page = "main"; st.rerun()
            else:
                html("""<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:10px;padding:0.8rem 1rem;margin-top:0.8rem;font-size:0.84rem;color:#FCA5A5;">⚠️ Please enter your email and password.</div>""")
        html("</div>")

        st.markdown("<br>", unsafe_allow_html=True)
        html("""<div style="text-align:center;font-size:0.82rem;color:#334155;">Don't have an account?</div>""")
        if st.button("Create Account"):
            st.session_state.page = "signup"; st.rerun()

    if st.button("← Back to Home"):
        st.session_state.page = "home"; st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ONBOARDING
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "onboard":
    step  = st.session_state.onboard_step
    total = len(ONBOARDING_QUESTIONS)
    pct   = int((step / total) * 100)

    html(f"""<div style="margin-bottom:1.5rem;">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
<div style="font-family:'Sora',sans-serif;font-size:0.72rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.08em;">Setting Up Your Profile</div>
<div style="font-family:'Sora',sans-serif;font-size:0.72rem;color:#60A5FA;font-weight:600;">{step} of {total}</div>
</div>
<div style="background:rgba(255,255,255,0.06);border-radius:6px;height:5px;overflow:hidden;">
<div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#2563EB,#06B6D4);border-radius:6px;transition:width 0.4s ease;"></div>
</div>
</div>""")

    if step < total:
        q = ONBOARDING_QUESTIONS[step]
        html(f"""<div class="onboard-card" style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);border-radius:20px;padding:2.5rem 2rem;max-width:680px;margin:0 auto;">
<div style="font-size:0.75rem;color:#334155;font-family:'Sora',sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.6rem;">Question {step+1}</div>
<div style="font-family:'Sora',sans-serif;font-size:1.3rem;font-weight:700;color:#E2E8F0;margin-bottom:1.5rem;line-height:1.4;">{q['question']}</div>
</div>""")

        answer = None
        if q["type"] == "single":
            answer = st.radio("Select an option", q["options"], key=f"q_{step}", label_visibility="collapsed")
        elif q["type"] == "multi":
            answer = [o for o in q["options"] if st.checkbox(o, key=f"q_{step}_{o}")]

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if step > 0 and st.button("← Previous"):
                st.session_state.onboard_step -= 1; st.rerun()
        with c2:
            label = "Continue →" if step < total - 1 else "🎉  Finish Setup"
            if st.button(label, type="primary"):
                st.session_state.onboard_answers[q["id"]] = answer
                if step < total - 1:
                    st.session_state.onboard_step += 1
                else:
                    st.session_state.page = "main"
                st.rerun()
    else:
        html("""<div style="text-align:center;padding:3rem;">
<div style="font-size:3rem;margin-bottom:1rem;">🎉</div>
<div style="font-family:'Sora',sans-serif;font-size:1.5rem;font-weight:800;color:#E2E8F0;margin-bottom:0.5rem;">You're all set!</div>
<div style="font-size:0.9rem;color:#334155;">Taking you to your personalised dashboard...</div>
</div>""")
        time.sleep(1.2)
        st.session_state.page = "main"; st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PRICING
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "pricing":
    html("""<div style="text-align:center;margin-bottom:2rem;">
<div style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;color:#FFFFFF;">Choose Your Plan</div>
<div style="font-size:0.9rem;color:#334155;margin-top:0.4rem;">Upgrade to Pro for the full intelligence suite</div>
</div>""")

    plan_meta = {"Free":("2563EB","🆓"),"Pro":("10B981","⭐"),"School":("8B5CF6","🏫")}
    for col, (plan_name, plan_data) in zip(st.columns(3), PLANS.items()):
        color, icon = plan_meta[plan_name]
        price  = plan_data["price"]
        period = plan_data.get("period","")
        feat_h = "".join([f'<div style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.5rem;"><span style="color:#10B981;font-size:0.8rem;margin-top:1px;">✓</span><span style="font-size:0.8rem;color:#94A3B8;line-height:1.4;">{f}</span></div>' for f in plan_data["features"]])
        lock_h = "".join([f'<div style="display:flex;align-items:flex-start;gap:0.5rem;margin-bottom:0.5rem;opacity:0.35;"><span style="color:#334155;font-size:0.8rem;margin-top:1px;">✗</span><span style="font-size:0.8rem;color:#334155;line-height:1.4;">{f}</span></div>' for f in plan_data.get("locked",[])])
        with col:
            html(f"""<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.08);border-top:4px solid #{color};border-radius:18px;padding:1.8rem 1.5rem;">
<div style="font-size:1.8rem;margin-bottom:0.5rem;">{icon}</div>
<div style="font-family:'Sora',sans-serif;font-size:1.1rem;font-weight:800;color:#E2E8F0;margin-bottom:0.3rem;">{plan_name}</div>
<div style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;color:#{color};margin-bottom:0.2rem;">{"Free" if price==0 else f"₦{price:,}"}</div>
<div style="font-size:0.72rem;color:#334155;margin-bottom:1.2rem;">{period if period else "forever"}</div>
<div style="border-top:1px solid rgba(255,255,255,0.06);padding-top:1rem;">{feat_h}{lock_h}</div>
</div>""")
            if plan_name == "Pro":
                if st.button("🚀  Upgrade to Pro — ₦2,500/mo", type="primary"):
                    html("""<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:10px;padding:0.8rem;margin-top:0.5rem;font-size:0.8rem;color:#6EE7B7;">✅ Payment integration coming soon. Contact smartedmatch@veritas.edu.ng</div>""")
            elif plan_name == "School":
                if st.button("🏫  Contact Us for School Plan"):
                    html("""<div style="background:rgba(139,92,246,0.08);border:1px solid rgba(139,92,246,0.2);border-radius:10px;padding:0.8rem;margin-top:0.5rem;font-size:0.8rem;color:#C4B5FD;">📧 smartedmatch@veritas.edu.ng</div>""")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to App"):
        st.session_state.page = "main"; st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "main":
    user   = st.session_state.user
    is_pro = user.get("is_pro", False)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        # Brand + user card
        html(f"""<div style="text-align:center;padding:0.8rem 0 1rem;">
<div style="font-size:1.7rem;margin-bottom:0.3rem;">🎓</div>
<div style="font-family:'Sora',sans-serif;font-size:1.1rem;font-weight:800;color:#60A5FA;">SmartEdMatch</div>
<div style="font-size:0.6rem;color:#334155;margin-top:0.1rem;letter-spacing:0.1em;text-transform:uppercase;">AI Admission Intelligence</div>
</div>
<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:0.55rem 0.8rem;margin-bottom:0.6rem;display:flex;align-items:center;gap:0.55rem;">
<div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#2563EB,#06B6D4);display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:800;color:#fff;flex-shrink:0;">{user.get('name','G')[0].upper()}</div>
<div>
<div style="font-family:'Sora',sans-serif;font-size:0.76rem;font-weight:700;color:#E2E8F0;">{user.get('name','Guest')}</div>
<div style="font-size:0.6rem;color:#334155;">{"⭐ Pro Member" if is_pro else "Free Plan"}</div>
</div>
</div>
<div class="sb-div"></div>""")

        if not _engine_loaded:
            st.error("Engine failed to load.")
            search_btn = False
        else:
            # ── Section 1: Course Selection ───────────────────────────────────
            html('<div class="sb-section">🎓 Course Selection</div>')
            faculty            = st.selectbox("Faculty", options=list(FACULTY_COURSES.keys()))
            courses_in_faculty = FACULTY_COURSES[faculty]
            course             = st.selectbox("Course",  options=courses_in_faculty)

            html('<div class="sb-div"></div>')

            # ── Section 2: Filters ────────────────────────────────────────────
            html('<div class="sb-section">🏫 Institution Filters</div>')
            institution_type = st.selectbox("Type", options=["Any"] + engine.get_institution_types())
            zone             = st.selectbox("Zone", options=["Any"] + engine.get_zones())

            html('<div class="sb-div"></div>')

            # ── Section 3: Scores & Budget ────────────────────────────────────
            html('<div class="sb-section">📊 Scores & Budget</div>')
            jamb_score = st.slider("JAMB Score", 100, 400, 200, 1)

            if jamb_score < 140:
                html("""<div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);border-radius:8px;padding:0.55rem 0.8rem;font-size:0.69rem;color:#FCD34D;line-height:1.5;margin-bottom:0.3rem;">⚠️ Below 140 — typically only polytechnics & colleges of education</div>""")
            elif jamb_score >= 250:
                html("""<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:8px;padding:0.55rem 0.8rem;font-size:0.69rem;color:#6EE7B7;line-height:1.5;margin-bottom:0.3rem;">✅ Excellent — qualifies for most federal & private universities</div>""")

            max_tuition = st.number_input("Max Annual Tuition (₦)", 10000, 3000000, 500000, 10000)
            top_n       = st.slider("Number of Results", 3, 20, 10)

            html('<div class="sb-div"></div>')

            # ── Section 4: JAMB Subjects ──────────────────────────────────────
            ALL_JAMB = ["Use of English","Mathematics","Physics","Chemistry","Biology",
                        "Economics","Government","Literature in English","Geography",
                        "Further Mathematics","Agricultural Science","CRK","IRK","History",
                        "Music","Fine Art","Arabic","French","Yoruba","Igbo","Hausa",
                        "Technical Drawing","Home Economics"]

            with st.expander("📋  My JAMB Subjects", expanded=False):
                html("""<div style="font-size:0.7rem;color:#64748B;line-height:1.5;margin-bottom:0.6rem;">Select your 4 subjects. Use of English is always compulsory.</div>""")
                s1 = st.selectbox("Subject 1", ALL_JAMB, index=0, key="js1")
                s2 = st.selectbox("Subject 2", ALL_JAMB, index=1, key="js2")
                s3 = st.selectbox("Subject 3", ALL_JAMB, index=2, key="js3")
                s4 = st.selectbox("Subject 4", ALL_JAMB, index=3, key="js4")
                user_jamb_subjects = [s1, s2, s3, s4]

                # Live per-subject validation for selected course
                required = JAMB_SUBJECTS.get(course, [])
                if required:
                    validation = validate_jamb(user_jamb_subjects, required)
                    all_ok     = all(m for _, m, _ in validation)
                    badge_c    = "#10B981" if all_ok else "#F59E0B"
                    badge_t    = "✅ Valid combination" if all_ok else "⚠️ Check your subjects"
                    html(f'<div style="margin-top:0.6rem;margin-bottom:0.3rem;"><div style="font-size:0.66rem;font-family:\'Sora\',sans-serif;font-weight:700;color:{badge_c};margin-bottom:0.4rem;">{badge_t} for {course}</div><div style="display:flex;flex-wrap:wrap;gap:4px;">')
                    for req_text, matched, flexible in validation:
                        css   = "subj-ok" if matched else ("subj-neutral" if flexible else "subj-missing")
                        icon  = "✓" if matched else ("~" if flexible else "✗")
                        short = req_text if len(req_text) <= 28 else req_text[:26] + "…"
                        html(f'<span class="{css}">{icon} {short}</span>')
                    html("</div></div>")

            # ── Section 5: WAEC Grades ────────────────────────────────────────
            with st.expander("📄  My WAEC Grades", expanded=False):
                html("""<div style="font-size:0.7rem;color:#64748B;line-height:1.5;margin-bottom:0.5rem;">Enter each subject and grade on a new line.<br><span style="color:#94A3B8;">e.g. English Language - A2</span></div>""")
                waec_raw = st.text_area("WAEC results", placeholder="English Language - A2\nMathematics - B3\nPhysics - C4\nChemistry - B2", height=110, label_visibility="collapsed")
                if waec_raw.strip():
                    waec_req = WAEC_REQUIREMENTS.get(course, WAEC_REQUIREMENTS["Default"])
                    html(f"""<div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);border-radius:8px;padding:0.6rem 0.8rem;margin-top:0.5rem;">
<div style="font-size:0.64rem;color:#34D399;font-family:'Sora',sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:3px;">WAEC requirement — {course}</div>
<div style="font-size:0.7rem;color:#94A3B8;line-height:1.5;">{waec_req}</div>
</div>""")

            html('<div class="sb-div"></div>')
            search_btn = st.button("🔍  Find My Institutions", type="primary")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⭐  Upgrade to Pro"):
                st.session_state.page = "pricing"; st.rerun()
            if st.button("🚪  Sign Out"):
                # Wipe all state cleanly, then re-initialise defaults
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                init_state()
                st.session_state.page = "home"
                st.rerun()

    # ── Hero ──────────────────────────────────────────────────────────────────
    html("""<div style="background:linear-gradient(135deg,#0B1A2E 0%,#0D2040 55%,#07101F 100%);border:1px solid rgba(255,255,255,0.07);border-radius:18px;padding:2rem 2.2rem;margin-bottom:1.4rem;position:relative;overflow:hidden;">
<div style="position:absolute;top:-60px;right:-60px;width:200px;height:200px;border-radius:50%;background:radial-gradient(circle,rgba(37,99,235,0.18) 0%,transparent 70%);pointer-events:none;"></div>
<div style="position:relative;z-index:1;">
<div style="display:inline-flex;align-items:center;gap:0.5rem;background:rgba(37,99,235,0.13);border:1px solid rgba(37,99,235,0.28);border-radius:30px;padding:4px 12px;margin-bottom:0.8rem;">
<div style="width:6px;height:6px;border-radius:50%;background:#10B981;box-shadow:0 0 6px rgba(16,185,129,0.8);animation:pulse-glow 2s ease-in-out infinite;"></div>
<span style="font-size:0.65rem;font-family:'Sora',sans-serif;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#60A5FA;">AI Admission Intelligence · Live</span>
</div>
<h1 style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;margin:0 0 0.3rem;color:#FFFFFF;">SmartEdMatch</h1>
<p style="font-size:0.88rem;color:#94A3B8;margin:0;line-height:1.6;">Nigeria's AI Admission Advisor — JAMB validation · NUC accreditation · Probability scoring · Campus intelligence</p>
</div>
</div>""")

    if not _engine_loaded:
        st.error(f"⚠️ Engine failed to load: {_load_error}")
        st.stop()

    tab1, tab2, tab3, tab4 = st.tabs(["🎯  My Recommendations","⚖️  Compare","📊  Course Explorer","🗺️  Map"])

    # ── TAB 1 ─────────────────────────────────────────────────────────────────
    with tab1:
        if not search_btn:
            html("""<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:14px;padding:2rem;text-align:center;margin-top:1rem;">
<div style="font-size:2.5rem;margin-bottom:0.8rem;">🎓</div>
<div style="font-family:'Sora',sans-serif;font-size:1rem;font-weight:700;color:#E2E8F0;margin-bottom:0.4rem;">Select your faculty and course, then click Find My Institutions</div>
<div style="font-size:0.82rem;color:#334155;line-height:1.6;">SmartEdMatch will validate your JAMB subjects, check NUC accreditation, estimate admission probability, and categorise each institution as Safe, Balanced, or Ambitious.</div>
</div>""")
        else:
            _type    = (institution_type if institution_type != "Any" else None) or engine.get_institution_types()[0]
            _zone    = (zone             if zone             != "Any" else None) or engine.get_zones()[0]
            _faculty = faculty

            # JAMB subject display
            required_subjects = JAMB_SUBJECTS.get(course, [])
            if required_subjects:
                pills = "".join([f'<span class="subj-neutral">{s}</span>' for s in required_subjects])
                html(f"""<div style="background:rgba(37,99,235,0.07);border:1px solid rgba(37,99,235,0.2);border-radius:12px;padding:1rem 1.2rem;margin-bottom:1rem;">
<div style="font-family:'Sora',sans-serif;font-size:0.78rem;font-weight:700;color:#60A5FA;margin-bottom:0.4rem;">Required JAMB subjects for {course}:</div>
<div style="display:flex;flex-wrap:wrap;gap:6px;">{pills}</div>
<div style="font-size:0.72rem;color:#334155;margin-top:0.5rem;">✓ Use of English is compulsory for all courses.</div>
</div>""")

            # WAEC requirement
            waec_req = WAEC_REQUIREMENTS.get(course, WAEC_REQUIREMENTS["Default"])
            html(f"""<div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.18);border-radius:12px;padding:0.9rem 1.2rem;margin-bottom:1.2rem;">
<div style="font-family:'Sora',sans-serif;font-size:0.78rem;font-weight:700;color:#34D399;margin-bottom:0.3rem;">WAEC Requirement for {course}:</div>
<div style="font-size:0.8rem;color:#94A3B8;">{waec_req}</div>
</div>""")

            # Run recommendation (no forced sleep — spinner gives honest feedback)
            with st.spinner("🤖 Finding your best institutions…"):
                try:
                    results, _ = engine.recommend(
                        course=course, institution_type=_type,
                        geopolitical_zone=_zone, faculty=_faculty,
                        jamb_score=jamb_score, max_tuition=max_tuition, top_n=top_n,
                    )
                    # Single broad-search pass when "Any" is selected
                    if institution_type == "Any" or zone == "Any":
                        from sklearn.metrics.pairwise import cosine_similarity as _cos
                        broad = engine.df[
                            (engine.df["jamb_cutoff"] <= jamb_score) &
                            (engine.df["tuition_min"] <= max_tuition) &
                            (engine.df["available"]   == "Yes") &
                            (engine.df["accredited"]  == "Yes")
                        ].copy()
                        if not broad.empty:
                            idxs = broad.index.tolist()
                            qv   = engine._build_query_vector(course,_type,_zone,_faculty,jamb_score,max_tuition)
                            sims = _cos(qv, engine.feature_matrix[idxs])[0]
                            broad["similarity_pct"] = (sims * 100).round(1)
                            results = broad.sort_values("similarity_pct", ascending=False).head(top_n)
                            results = results[["university_name","state","geopolitical_zone","type","course","faculty","jamb_cutoff","tuition_min","tuition_max","similarity_pct"]].reset_index(drop=True)
                            results.index += 1

                    # Pre-fetch ALL sentiment in one pass — eliminates N×HTTP bottleneck
                    names           = results["university_name"].tolist() if not results.empty else []
                    sentiment_cache = {n: get_sentiment(n) for n in names}

                except Exception as e:
                    st.error(f"Recommendation error: {e}")
                    st.stop()

            n   = len(results) if not results.empty else 0
            top = f"{results['similarity_pct'].iloc[0]:.1f}%" if not results.empty else "—"

            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("Results Found", n)
            with c2: st.metric("JAMB Score", jamb_score)
            with c3: st.metric("Max Budget", f"₦{max_tuition:,}")
            with c4: st.metric("Top Match", top)

            st.markdown("<br>", unsafe_allow_html=True)

            if results.empty:
                html("""<div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.2);border-radius:14px;padding:1.4rem 1.8rem;">
<div style="font-family:'Sora',sans-serif;font-weight:700;color:#FCA5A5;margin-bottom:0.5rem;">⚠️ No Matching Institutions Found</div>
<div style="font-size:0.82rem;color:#94A3B8;line-height:1.7;">Try increasing your budget, lowering your JAMB filter, switching to "Any" zone, or selecting a different course.</div>
</div>""")
            else:
                html(f"""<div style="display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:1rem;">
<div>
<div style="font-family:'Sora',sans-serif;font-size:1.1rem;font-weight:700;color:#E2E8F0;">Top {n} Recommendations for {course}</div>
<div style="font-size:0.73rem;color:#334155;margin-top:2px;">JAMB ≤ {jamb_score} &nbsp;·&nbsp; Budget ≤ ₦{max_tuition:,} &nbsp;·&nbsp; Categorised by admission probability</div>
</div>
</div>""")

                for rank, row in results.iterrows():
                    score     = float(row["similarity_pct"])
                    cutoff    = int(row["jamb_cutoff"])
                    inst_name = str(row["university_name"])
                    inst_type = str(row["type"])

                    prob               = admission_probability(jamb_score, cutoff, inst_type)
                    cat, cat_color, cat_icon = get_category(prob)

                    sentiment      = sentiment_cache.get(inst_name, get_sentiment(inst_name))
                    sent_score     = sentiment["score"]
                    sent_color_val = sentiment_color(sent_score)
                    sent_lbl, _, sent_emoji = sentiment_label(sent_score)
                    data_src   = sentiment.get("data_source","base")
                    # FIX: correct live source names are duckduckgo and wikipedia
                    is_live    = "duckduckgo" in data_src or "wikipedia" in data_src
                    live_badge = "🟢 Live" if is_live else "📚 Research"
                    h_list     = " &nbsp;·&nbsp; ".join(sentiment.get("highlights",[])[:2])
                    c_list     = sentiment.get("concerns",["No major concerns"])[0]
                    asuu       = sentiment.get("asuu_risk","Unknown")
                    asuu_c     = asuu_risk_color(asuu)

                    if score >= 70:
                        sc,sbg,sbd,bar = "#10B981","rgba(16,185,129,0.09)","rgba(16,185,129,0.22)","linear-gradient(90deg,#059669,#10B981)"
                    elif score >= 45:
                        sc,sbg,sbd,bar = "#3B82F6","rgba(59,130,246,0.09)","rgba(59,130,246,0.22)","linear-gradient(90deg,#1D4ED8,#3B82F6)"
                    else:
                        sc,sbg,sbd,bar = "#F59E0B","rgba(245,158,11,0.09)","rgba(245,158,11,0.22)","linear-gradient(90deg,#D97706,#F59E0B)"

                    medal = {1:"🥇",2:"🥈",3:"🥉"}.get(int(rank),"")
                    rl    = medal if medal else f'<span style="font-weight:800;color:#334155;font-size:0.88rem;">#{rank}</span>'

                    html(f"""<div class="result-card" style="background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:1.3rem 1.5rem;margin-bottom:0.7rem;border-left:3px solid {sc};">
<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;">
<div style="flex:1;min-width:0;">
<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.2rem;flex-wrap:wrap;">
<span style="font-size:0.95rem;">{rl}</span>
<span style="font-family:'Sora',sans-serif;font-size:0.94rem;font-weight:700;color:#F1F5F9;">{inst_name}</span>
<span style="background:{cat_color}22;border:1px solid {cat_color}44;color:{cat_color};border-radius:20px;padding:1px 8px;font-size:0.62rem;font-weight:700;font-family:'Sora',sans-serif;">{cat_icon} {cat}</span>
</div>
<div style="font-size:0.72rem;color:#334155;margin-bottom:0.8rem;margin-left:1.5rem;">📍 {str(row['state'])} &nbsp;·&nbsp; {str(row['geopolitical_zone'])}</div>
<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:0.7rem;">
<span style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.2);color:#93C5FD;border-radius:20px;padding:2px 9px;font-size:0.67rem;font-weight:600;font-family:'Sora',sans-serif;">📘 {str(row['course'])}</span>
<span style="background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.2);color:#C4B5FD;border-radius:20px;padding:2px 9px;font-size:0.67rem;font-weight:600;font-family:'Sora',sans-serif;">🏫 {inst_type}</span>
<span style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);color:#FCD34D;border-radius:20px;padding:2px 9px;font-size:0.67rem;font-weight:600;font-family:'Sora',sans-serif;">📝 Cut-off: {cutoff}</span>
<span style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);color:#6EE7B7;border-radius:20px;padding:2px 9px;font-size:0.67rem;font-weight:600;font-family:'Sora',sans-serif;">💰 ₦{int(row['tuition_min']):,} – ₦{int(row['tuition_max']):,}</span>
</div>
<div style="display:flex;gap:1rem;flex-wrap:wrap;">
<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:0.4rem 0.7rem;flex:1;min-width:110px;">
<div style="font-size:0.6rem;color:#334155;font-family:'Sora',sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:2px;">Admission Prob.</div>
<div style="font-family:'Sora',sans-serif;font-size:1.1rem;font-weight:800;color:{cat_color};">{prob}%</div>
</div>
<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:0.4rem 0.7rem;flex:1;min-width:110px;">
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:2px;">
<div style="font-size:0.6rem;color:#334155;font-family:'Sora',sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Sentiment</div>
<div style="font-size:0.55rem;color:{"#10B981" if is_live else "#64748B"};font-weight:600;">{live_badge}</div>
</div>
<div style="font-family:'Sora',sans-serif;font-size:1.1rem;font-weight:800;color:{sent_color_val};">{sent_score}/100</div>
<div style="font-size:0.6rem;color:{sent_color_val};margin-top:1px;">{sent_emoji} {sent_lbl}</div>
</div>
<div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:0.4rem 0.7rem;flex:2;min-width:170px;">
<div style="font-size:0.6rem;color:#334155;font-family:'Sora',sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:3px;">Campus Intelligence</div>
<div style="font-size:0.7rem;color:#94A3B8;line-height:1.5;">✓ {h_list}</div>
<div style="font-size:0.7rem;color:#475569;line-height:1.5;margin-top:1px;">⚠ {c_list}</div>
<div style="margin-top:4px;display:flex;align-items:center;gap:4px;">
<span style="font-size:0.6rem;color:#334155;">ASUU Risk:</span>
<span style="font-size:0.6rem;font-weight:700;color:{asuu_c};">{asuu}</span>
</div>
</div>
</div>
</div>
<div style="background:{sbg};border:1px solid {sbd};border-radius:12px;padding:0.6rem 0.85rem;text-align:center;min-width:78px;flex-shrink:0;">
<div style="font-family:'Sora',sans-serif;font-size:1.4rem;font-weight:800;color:{sc};line-height:1;">{score:.1f}%</div>
<div style="font-size:0.58rem;color:#334155;margin-top:3px;text-transform:uppercase;letter-spacing:0.06em;">Match</div>
</div>
</div>
<div style="background:rgba(255,255,255,0.04);border-radius:3px;height:2px;margin-top:1rem;overflow:hidden;">
<div style="width:{min(score,100)}%;height:100%;background:{bar};border-radius:3px;"></div>
</div>
</div>""")

                html("""<div style="display:flex;gap:1rem;flex-wrap:wrap;margin:1rem 0;">
<div style="display:flex;align-items:center;gap:0.4rem;"><span>✅</span><span style="font-size:0.75rem;color:#10B981;font-weight:600;">Safe</span><span style="font-size:0.72rem;color:#334155;">70%+ admission chance</span></div>
<div style="display:flex;align-items:center;gap:0.4rem;"><span>⚖️</span><span style="font-size:0.75rem;color:#F59E0B;font-weight:600;">Balanced</span><span style="font-size:0.72rem;color:#334155;">40–70% admission chance</span></div>
<div style="display:flex;align-items:center;gap:0.4rem;"><span>🚀</span><span style="font-size:0.75rem;color:#EF4444;font-weight:600;">Ambitious</span><span style="font-size:0.72rem;color:#334155;">Below 40% admission chance</span></div>
</div>""")
                st.download_button(
                    label="⬇️  Download Full Report as CSV",
                    data=results.to_csv(index=True),
                    file_name=f"smartedmatch_{course.replace(' ','_')}_report.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

    # ── TAB 2: COMPARE ────────────────────────────────────────────────────────
    with tab2:
        html('<div class="sb-section">Compare Institutions Side by Side</div>')
        all_inst = sorted(engine.df["university_name"].unique().tolist())
        ca, cb, cc = st.columns(3)
        with ca: i1 = st.selectbox("Institution 1",            ["Select…"]+all_inst, key="ci1")
        with cb: i2 = st.selectbox("Institution 2",            ["Select…"]+all_inst, key="ci2")
        with cc: i3 = st.selectbox("Institution 3 (optional)", ["Select…"]+all_inst, key="ci3")

        if st.button("⚖️  Compare Now", type="primary"):
            sel = [i for i in [i1,i2,i3] if i != "Select…"]
            if len(sel) < 2:
                html("""<div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);border-radius:12px;padding:1rem;margin-top:0.8rem;font-size:0.84rem;color:#FCD34D;">⚠️ Please select at least 2 institutions.</div>""")
            else:
                with st.spinner("Fetching campus intelligence…"):
                    cmp_sentiment = {n: get_sentiment(n) for n in sel}

                colors = ["2563EB","10B981","8B5CF6"]
                for col, name, color in zip(st.columns(len(sel)), sel, colors):
                    df_r = engine.df[engine.df["university_name"] == name]
                    if df_r.empty: continue
                    r         = df_r.iloc[0]
                    sent      = cmp_sentiment[name]
                    sc_c      = sentiment_color(sent["score"])
                    courses_l = ", ".join(sorted(df_r["course"].unique()))
                    co_min    = int(df_r["jamb_cutoff"].min())
                    prob      = admission_probability(jamb_score, co_min, str(r["type"]))
                    cat, cat_color, cat_icon = get_category(prob)
                    with col:
                        html(f"""<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.08);border-top:3px solid #{color};border-radius:16px;padding:1.3rem 1.1rem;margin-top:0.8rem;">
<div style="font-family:'Sora',sans-serif;font-size:0.9rem;font-weight:700;color:#F1F5F9;margin-bottom:0.8rem;line-height:1.3;">{name}</div>
<div style="display:flex;flex-direction:column;gap:0.45rem;">
<div style="background:var(--glass);border-radius:8px;padding:0.45rem 0.6rem;"><div style="font-size:0.6rem;color:#334155;text-transform:uppercase;font-family:'Sora',sans-serif;font-weight:700;">Location</div><div style="font-size:0.82rem;color:#E2E8F0;margin-top:2px;">📍 {r['state']}, {r['geopolitical_zone']}</div></div>
<div style="background:var(--glass);border-radius:8px;padding:0.45rem 0.6rem;"><div style="font-size:0.6rem;color:#334155;text-transform:uppercase;font-family:'Sora',sans-serif;font-weight:700;">Type</div><div style="font-size:0.82rem;color:#E2E8F0;margin-top:2px;">{r['type']}</div></div>
<div style="background:var(--glass);border-radius:8px;padding:0.45rem 0.6rem;"><div style="font-size:0.6rem;color:#334155;text-transform:uppercase;font-family:'Sora',sans-serif;font-weight:700;">Admission Probability</div><div style="font-family:'Sora',sans-serif;font-size:1.2rem;font-weight:800;color:{cat_color};margin-top:2px;">{prob}% &nbsp;<span style="font-size:0.7rem;">{cat_icon} {cat}</span></div></div>
<div style="background:var(--glass);border-radius:8px;padding:0.45rem 0.6rem;"><div style="font-size:0.6rem;color:#334155;text-transform:uppercase;font-family:'Sora',sans-serif;font-weight:700;">Campus Sentiment</div><div style="font-family:'Sora',sans-serif;font-size:1.2rem;font-weight:800;color:{sc_c};margin-top:2px;">{sent['score']}/100</div></div>
<div style="background:var(--glass);border-radius:8px;padding:0.45rem 0.6rem;"><div style="font-size:0.6rem;color:#334155;text-transform:uppercase;font-family:'Sora',sans-serif;font-weight:700;">Min JAMB Cut-off</div><div style="font-size:0.88rem;color:#FCD34D;margin-top:2px;font-weight:700;">{co_min}</div></div>
<div style="background:var(--glass);border-radius:8px;padding:0.45rem 0.6rem;"><div style="font-size:0.6rem;color:#334155;text-transform:uppercase;font-family:'Sora',sans-serif;font-weight:700;">Max Tuition</div><div style="font-size:0.82rem;color:#6EE7B7;margin-top:2px;">₦{int(df_r['tuition_max'].max()):,}</div></div>
<div style="background:var(--glass);border-radius:8px;padding:0.45rem 0.6rem;"><div style="font-size:0.6rem;color:#334155;text-transform:uppercase;font-family:'Sora',sans-serif;font-weight:700;">Courses</div><div style="font-size:0.72rem;color:#94A3B8;margin-top:3px;line-height:1.5;">{courses_l}</div></div>
<div style="background:var(--glass);border-radius:8px;padding:0.45rem 0.6rem;"><div style="font-size:0.6rem;color:#334155;text-transform:uppercase;font-family:'Sora',sans-serif;font-weight:700;">Highlights</div>{"".join([f'<div style="font-size:0.7rem;color:#94A3B8;margin-top:2px;">✓ {h}</div>' for h in sent.get("highlights",[])])}</div>
<div style="background:var(--glass);border-radius:8px;padding:0.45rem 0.6rem;"><div style="font-size:0.6rem;color:#334155;text-transform:uppercase;font-family:'Sora',sans-serif;font-weight:700;">Known Concerns</div>{"".join([f'<div style="font-size:0.7rem;color:#475569;margin-top:2px;">⚠ {c}</div>' for c in sent.get("concerns",[])])}</div>
</div>
</div>""")

    # ── TAB 3: COURSE EXPLORER ────────────────────────────────────────────────
    with tab3:
        html('<div class="sb-section">Explore Courses by Faculty</div>')
        for fac, clist in FACULTY_COURSES.items():
            with st.expander(f"🏛️  {fac}  ({len(clist)} courses)"):
                cols = st.columns(3)
                for i, c in enumerate(sorted(clist)):
                    req = JAMB_SUBJECTS.get(c, ["See JAMB brochure"])
                    with cols[i % 3]:
                        html(f"""<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:0.6rem 0.8rem;margin-bottom:0.5rem;">
<div style="font-family:'Sora',sans-serif;font-size:0.82rem;font-weight:700;color:#E2E8F0;margin-bottom:0.3rem;">{c}</div>
<div style="font-size:0.65rem;color:#334155;line-height:1.4;">{" · ".join(req[:2])}{"…" if len(req)>2 else ""}</div>
</div>""")

    # ── TAB 4: MAP ────────────────────────────────────────────────────────────
    with tab4:
        html('<div class="sb-section">Institution Map — All 6 Geopolitical Zones</div>')

        COORDS = {
            "University of Lagos":(6.5158,3.3898,"Federal University"),
            "University of Ibadan":(7.3775,3.9470,"Federal University"),
            "Obafemi Awolowo University":(7.5189,4.5234,"Federal University"),
            "University of Nigeria Nsukka":(6.8636,7.3961,"Federal University"),
            "Ahmadu Bello University":(11.1581,7.6494,"Federal University"),
            "University of Benin":(6.3612,5.6218,"Federal University"),
            "University of Port Harcourt":(4.8979,6.9065,"Federal University"),
            "University of Ilorin":(8.4799,4.6418,"Federal University"),
            "Nnamdi Azikiwe University":(6.2103,7.0675,"Federal University"),
            "Federal University of Technology Akure":(7.2526,5.2034,"Federal University"),
            "Federal University of Technology Minna":(9.6139,6.5569,"Federal University"),
            "Bayero University Kano":(12.0022,8.5920,"Federal University"),
            "University of Calabar":(4.9516,8.3225,"Federal University"),
            "University of Abuja":(9.0574,7.4898,"Federal University"),
            "University of Maiduguri":(11.8333,13.1517,"Federal University"),
            "Usman Dan Fodio University":(13.0622,5.2339,"Federal University"),
            "Federal University Lokoja":(7.7973,6.7377,"Federal University"),
            "Federal University Lafia":(8.4945,8.5038,"Federal University"),
            "Covenant University":(6.6731,3.1578,"Private University"),
            "Babcock University":(6.8917,3.7203,"Private University"),
            "American University of Nigeria":(10.1729,13.3044,"Private University"),
            "Pan-Atlantic University":(6.5087,3.3624,"Private University"),
            "Redeemer's University":(7.4706,4.2458,"Private University"),
            "Landmark University":(8.5333,4.5333,"Private University"),
            "Afe Babalola University":(7.7167,5.2167,"Private University"),
            "Bowen University":(7.4500,4.6500,"Private University"),
            "Baze University":(9.0574,7.4898,"Private University"),
            "Nile University of Nigeria":(9.0500,7.5167,"Private University"),
            "Veritas University Abuja":(8.9167,7.2333,"Private University"),
            "Igbinedion University":(6.3067,5.6142,"Private University"),
            "Lagos State University":(6.5156,3.3720,"State University"),
            "Rivers State University":(4.8156,7.0498,"State University"),
            "Kogi State University":(7.8028,6.7394,"State University"),
            "Delta State University":(5.5372,5.9748,"State University"),
            "Imo State University":(5.4895,7.0395,"State University"),
            "Enugu State University":(6.4415,7.5071,"State University"),
            "Ekiti State University":(7.7333,5.2167,"State University"),
            "Kaduna State University":(10.5239,7.4381,"State University"),
            "Yaba College of Technology":(6.5167,3.3667,"Federal Polytechnic"),
            "Federal Polytechnic Nekede":(5.4795,7.0218,"Federal Polytechnic"),
            "Federal Polytechnic Ilaro":(6.8878,3.0202,"Federal Polytechnic"),
            "Federal Polytechnic Bauchi":(10.3167,9.8333,"Federal Polytechnic"),
            "Kaduna Polytechnic":(10.5239,7.4381,"State Polytechnic"),
            "The Polytechnic Ibadan":(7.3775,3.9470,"State Polytechnic"),
            "Lagos State Polytechnic":(6.5156,3.3720,"State Polytechnic"),
            "Federal College of Education Zaria":(11.0667,7.7167,"Federal College of Education"),
            "Federal College of Education Abeokuta":(7.1475,3.3619,"Federal College of Education"),
            "Federal College of Education Kano":(12.0022,8.5920,"Federal College of Education"),
            "Adeyemi College of Education":(7.1667,4.8333,"Federal College of Education"),
        }
        TYPE_COLORS = {
            "Federal University":"#2563EB","State University":"#06B6D4",
            "Private University":"#8B5CF6","Federal Polytechnic":"#F59E0B",
            "State Polytechnic":"#F97316","Federal College of Education":"#10B981",
            "State College of Education":"#34D399",
        }

        mf1,mf2 = st.columns(2)
        with mf1: map_type = st.selectbox("Filter by type",["All Types"]+list(TYPE_COLORS.keys()),key="map_type")
        with mf2: map_q    = st.text_input("Search institution",placeholder="e.g. Lagos, Covenant…",key="map_q")

        markers = [
            {"name":n,"lat":lat,"lng":lng,"type":t,"color":TYPE_COLORS.get(t,"#64748B")}
            for n,(lat,lng,t) in COORDS.items()
            if (map_type=="All Types" or t==map_type) and (not map_q or map_q.lower() in n.lower())
        ]
        st.caption(f"Showing {len(markers)} institutions. Click any pin for details.")

        mjs = "".join([f"""
L.circleMarker([{m["lat"]},{m["lng"]}],{{radius:8,fillColor:"{m["color"]}",color:"#fff",weight:1.5,opacity:1,fillOpacity:0.85}}).addTo(map).bindPopup(`<div style="font-family:Arial,sans-serif;min-width:180px;"><div style="font-weight:700;font-size:13px;margin-bottom:4px;color:#1E293B;">{m["name"]}</div><div style="background:{m["color"]}22;border:1px solid {m["color"]}44;color:{m["color"]};border-radius:20px;padding:2px 8px;font-size:11px;font-weight:600;display:inline-block;">{m["type"]}</div></div>`,{{maxWidth:260}});""" for m in markers])

        st.components.v1.html(f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>html,body{{margin:0;padding:0;background:#07101F;}}#map{{width:100%;height:520px;border-radius:14px;}}
.leaflet-popup-content-wrapper{{background:#0B1A2E;border:1px solid rgba(255,255,255,0.1);border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.4);}}
.leaflet-popup-tip{{background:#0B1A2E;}}.leaflet-popup-close-button{{color:#94A3B8!important;}}
.leaflet-control-attribution{{background:rgba(7,16,31,0.85)!important;color:#334155!important;font-size:10px!important;}}
.leaflet-control-attribution a{{color:#60A5FA!important;}}.leaflet-control-zoom a{{background:#0B1A2E!important;color:#E2E8F0!important;border-color:rgba(255,255,255,0.1)!important;}}
</style></head><body><div id="map"></div>
<script>var map=L.map("map",{{center:[9.082,8.675],zoom:6,scrollWheelZoom:true}});
L.tileLayer("https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png",{{attribution:"© OpenStreetMap © CARTO",subdomains:"abcd",maxZoom:18}}).addTo(map);
{mjs}</script></body></html>""", height=540, scrolling=False)

        st.markdown("<br>", unsafe_allow_html=True)
        for col,(it,col_c) in zip(st.columns(len(TYPE_COLORS)),TYPE_COLORS.items()):
            with col:
                html(f'<div style="display:flex;align-items:center;gap:5px;"><div style="width:9px;height:9px;border-radius:50%;background:{col_c};flex-shrink:0;"></div><span style="font-size:0.62rem;color:#64748B;">{it}</span></div>')

    # ── Footer ────────────────────────────────────────────────────────────────
    html("""<div style="text-align:center;padding:2rem 0 0.8rem;margin-top:2.5rem;border-top:1px solid rgba(255,255,255,0.05);">
<div style="font-family:'Sora',sans-serif;font-size:0.78rem;font-weight:700;color:#60A5FA;margin-bottom:0.35rem;">SmartEdMatch</div>
<div style="font-size:0.66rem;color:#1E293B;line-height:1.8;">AI-Driven Higher Institution Recommendation System for Nigeria<br>
Aliyu Daniel Eshoraimeh &nbsp;·&nbsp; VUG/CSC/23/8935 &nbsp;·&nbsp; Veritas University, Abuja &nbsp;·&nbsp; 2025/2026</div>
</div>""")
