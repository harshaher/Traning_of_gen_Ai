"""
ui/app.py - ShellSathi Streamlit Web Application (Day 14)
Linux Command Assistant with Terminal-Themed Authentication & Streamlined Dashboard

Project Name: ShellSathi
Tagline: Intelligent Linux Command Assistant (SJ-62)
"""

import os
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
current_dir = str(Path(__file__).resolve().parent)
sys.path = [p for p in sys.path if os.path.abspath(p) != os.path.abspath(current_dir)]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if "app" in sys.modules and not hasattr(sys.modules["app"], "__path__"):
    del sys.modules["app"]

from app.auth import (
    authenticate_user,
    init_user_db,
    register_user,
    reset_password,
)
from app.placeholder import (
    extract_placeholders,
    fill_template,
    find_command_templates,
    has_placeholders,
)

# ------------------------------------------------------------------------------
# 1. Page Configuration & Terminal Theme Styling
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="ShellSathi - Intelligent Linux Command Assistant (SJ-62)",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Dark Terminal Theme Styling */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .auth-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-top: 3px solid #00ff66;
        border-radius: 10px;
        padding: 28px 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 255, 102, 0.1);
        margin-top: 10px;
        margin-bottom: 24px;
    }
    .auth-title {
        font-family: 'Courier New', Courier, monospace;
        color: #00ff66;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 2px;
    }
    .auth-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 14px;
    }
    .terminal-badge {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.8rem;
        color: #00ff66;
        background: rgba(0, 255, 102, 0.08);
        border: 1px solid rgba(0, 255, 102, 0.25);
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 18px;
    }
    .user-badge {
        background: #111827;
        border-left: 3px solid #00ff66;
        padding: 10px 16px;
        border-radius: 6px;
        margin-bottom: 16px;
        font-size: 0.9rem;
        color: #cbd5e1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------------------
# 2. Core Backend Communication & Health Probing
# ------------------------------------------------------------------------------
def get_backend_url() -> str:
    """Retrieve backend URL from session state or environment variable."""
    if "backend_url" in st.session_state and st.session_state.backend_url:
        url = st.session_state.backend_url.strip().rstrip("/")
    else:
        env_url = os.environ.get("BACKEND_URL", "").strip().rstrip("/")
        if env_url:
            url = env_url
        else:
            is_cloud = bool(os.environ.get("RENDER") or os.environ.get("PORT") == "8501")
            url = "https://shellsathi-api.onrender.com" if is_cloud else "http://127.0.0.1:8000"

    if not (url.startswith("http://") or url.startswith("https://")):
        if any(h in url for h in ("127.0.0.1", "localhost", "api:")):
            url = f"http://{url}"
        else:
            url = f"https://{url}"

    clean_host = url.split("://")[-1].split(":")[0]
    if "." not in clean_host and clean_host not in ("localhost", "api"):
        url = f"https://{clean_host}.onrender.com"

    return url


def check_backend_health(base_url: str, timeout: float = 12.0) -> Dict[str, Any]:
    """
    Query FastAPI /health with progressive retries for cloud cold starts.
    Accurately distinguishes online, cold start, and offline states.
    """
    clean_url = base_url.rstrip("/")
    for attempt in range(2):
        try:
            resp = requests.get(f"{clean_url}/health", timeout=timeout)
            if resp.status_code == 200:
                return {
                    "online": True,
                    "status_code": 200,
                    "data": resp.json(),
                    "is_cold_start": False,
                    "error": "",
                }
            if resp.status_code in (502, 503, 504):
                if attempt == 0:
                    time.sleep(2)
                    continue
                return {
                    "online": False,
                    "status_code": resp.status_code,
                    "data": {},
                    "is_cold_start": True,
                    "error": f"HTTP {resp.status_code} (Cloud instance is booting or waking up)",
                }
            return {
                "online": False,
                "status_code": resp.status_code,
                "data": {},
                "is_cold_start": False,
                "error": f"HTTP {resp.status_code}",
            }
        except requests.exceptions.Timeout:
            if attempt == 0:
                time.sleep(1)
                continue
            return {
                "online": False,
                "status_code": 0,
                "data": {},
                "is_cold_start": True,
                "error": "Connection timed out (Instance waking up from idle sleep)",
            }
        except requests.exceptions.ConnectionError as exc:
            err_msg = str(exc)
            is_cold = any(
                k in err_msg.lower()
                for k in ["failed to resolve", "name or service not known", "reset", "refused"]
            )
            if attempt == 0 and is_cold:
                time.sleep(2)
                continue
            return {
                "online": False,
                "status_code": 0,
                "data": {},
                "is_cold_start": is_cold,
                "error": "Connection failed" if not is_cold else "Cloud instance initializing",
            }
        except Exception as exc:
            return {
                "online": False,
                "status_code": 0,
                "data": {},
                "is_cold_start": False,
                "error": str(exc),
            }
    return {
        "online": False,
        "status_code": 0,
        "data": {},
        "is_cold_start": True,
        "error": "Backend unreachable",
    }


def _pinger_worker(backend_url: str) -> None:
    """Periodically ping backend /health every 10 minutes to prevent Render free-tier idle sleep."""
    while True:
        try:
            requests.get(f"{backend_url}/health", timeout=15)
        except Exception:
            pass
        time.sleep(600)


def start_keep_alive_pinger(backend_url: str) -> None:
    """Start background keep-alive thread to keep Render backend awake."""
    if not backend_url or "localhost" in backend_url or "127.0.0.1" in backend_url:
        return
    if not getattr(st, "_pinger_started", False):
        t = threading.Thread(target=_pinger_worker, args=(backend_url,), daemon=True)
        t.start()
        st._pinger_started = True


def send_ask_request(base_url: str, question: str, top_k: int = 3) -> Dict[str, Any]:
    """Call POST /ask endpoint (Mode 1: RAG) with transient retry handling."""
    url = f"{base_url.rstrip('/')}/ask"
    payload = {"question": question, "top_k": top_k}
    for attempt in range(2):
        try:
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code in (502, 503, 504) and attempt == 0:
                time.sleep(3)
                continue
            resp.raise_for_status()
            return resp.json()
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as err:
            if attempt == 0:
                time.sleep(3)
                continue
            raise err


def send_agent_request(
    base_url: str,
    question: Optional[str] = None,
    approved: Optional[bool] = None,
    thread_id: str = "default_user",
) -> Dict[str, Any]:
    """Call POST /agent endpoint (Mode 2: LangGraph Agent) with transient retry handling."""
    url = f"{base_url.rstrip('/')}/agent"
    payload: Dict[str, Any] = {"thread_id": thread_id}
    if question is not None:
        payload["question"] = question
    if approved is not None:
        payload["approved"] = approved
    for attempt in range(2):
        try:
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code in (502, 503, 504) and attempt == 0:
                time.sleep(3)
                continue
            resp.raise_for_status()
            return resp.json()
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as err:
            if attempt == 0:
                time.sleep(3)
                continue
            raise err


def submit_feedback_api(
    base_url: str,
    question: str,
    answer: str,
    rating: str,
    thread_id: Optional[str] = None,
) -> bool:
    """Call POST /feedback endpoint to persist rating."""
    url = f"{base_url.rstrip('/')}/feedback"
    payload = {
        "question": question,
        "answer": answer,
        "rating": rating,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "thread_id": thread_id,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False


def render_placeholder_filler(template: str, widget_key_prefix: str) -> None:
    """Renders interactive widget to fill Linux command placeholders (e.g. {{source}}, {{dest}})."""
    placeholders = extract_placeholders(template)
    if not placeholders:
        return

    with st.expander("🛠️ Interactive Command Builder (Placeholder Filler)", expanded=True):
        st.markdown("**Template detected:**")
        st.code(template, language="bash")
        st.caption(
            "Provide your values below to instantly generate your ready-to-run Linux command:"
        )

        cols = st.columns(min(len(placeholders), 3))
        user_values = {}
        for idx, ph in enumerate(placeholders):
            col = cols[idx % len(cols)]
            input_val = col.text_input(
                f"`{ph}`:",
                key=f"{widget_key_prefix}_{ph}",
                placeholder=f"Enter {ph}...",
            )
            user_values[ph] = input_val

        completed_command = fill_template(template, user_values, default_to_placeholder=True)

        st.markdown("**Your Ready-to-Run Command:**")
        st.code(completed_command, language="bash")


LINUX_SPECIFIC_COMMANDS = {"top", "journalctl", "systemctl"}


def get_working_doc_url(src: str) -> str:
    """Return a verified, working web documentation URL for the command."""
    clean = src.strip()
    if "tldr.sh/linux/" in clean:
        cmd = clean.split("tldr.sh/linux/")[-1].strip("/")
        folder = "linux" if cmd in LINUX_SPECIFIC_COMMANDS else "common"
        return f"https://github.com/tldr-pages/tldr/blob/main/pages/{folder}/{cmd}.md"
    if "raw.githubusercontent.com/tldr-pages/tldr/main/" in clean:
        return clean.replace(
            "raw.githubusercontent.com/tldr-pages/tldr/main/",
            "github.com/tldr-pages/tldr/blob/main/",
        )
    return clean


def render_citations(sources: Optional[List[str]]) -> None:
    """Render verified source citations with clickable hyperlinks that actually work."""
    valid_sources = [s.strip() for s in (sources or []) if s and isinstance(s, str) and s.strip()]
    if valid_sources:
        with st.expander("📚 Supporting Citations & Documentation Sources", expanded=False):
            for raw_src in valid_sources:
                working_url = get_working_doc_url(raw_src)
                if working_url.startswith("http://") or working_url.startswith("https://"):
                    if "github.com/tldr-pages/tldr" in working_url:
                        cmd = working_url.split("/")[-1].replace(".md", "")
                        label = f"Official TLDR Documentation: `{cmd}`"
                    elif "man7.org" in working_url:
                        label = "Linux man-pages Reference"
                    else:
                        label = working_url
                    st.markdown(f"- 📄 [{label}]({working_url})")
                else:
                    st.markdown(f"- 📄 `{raw_src}`")


# ------------------------------------------------------------------------------
# 3. Session State Initialization
# ------------------------------------------------------------------------------
init_user_db()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"user_{uuid.uuid4().hex[:8]}"

if "feedback_status" not in st.session_state:
    st.session_state.feedback_status = {}

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None


# ------------------------------------------------------------------------------
# 4. Authentication Gatekeeper (Login / Sign Up / Forgot Password)
# ------------------------------------------------------------------------------
if not st.session_state.authenticated:
    col_left, col_center, col_right = st.columns([1, 1.8, 1])

    with col_center:
        st.markdown(
            """
            <div class="auth-card">
                <div class="auth-title">🐧 ShellSathi</div>
                <div class="auth-subtitle">Intelligent Linux Command Assistant (SJ-62)</div>
                <div class="terminal-badge">● shellsathi-security.service - Terminal Access Gateway</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        show_pwd = st.checkbox("👁️ Show Password", key="auth_toggle_pwd")
        pwd_input_type = "default" if show_pwd else "password"

        # ----------------- VIEW 1: LOGIN -----------------
        if st.session_state.auth_mode == "login":
            st.markdown("### 🔑 Terminal Authentication")
            st.caption(
                "Sign in with your registered ShellSathi credentials to access the terminal."
            )

            login_email = st.text_input(
                "📧 Terminal User / Email:", placeholder="e.g. harsh@shellsathi.com"
            )
            login_password = st.text_input(
                "🔒 Password:",
                type=pwd_input_type,
                placeholder="Enter your password...",
            )

            if st.button("⚡ Login to ShellSathi", type="primary", use_container_width=True):
                user, msg = authenticate_user(login_email, login_password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success(f"Access granted! Welcome, {user['full_name']}.")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

            st.caption(
                "💡 Presentation accounts: `harsh@shellsathi.com` (`Harsh@123`) or `admin@shellsathi.com` (`Admin@123`)"
            )
            st.markdown("---")

            nav_col1, nav_col2 = st.columns(2)
            if nav_col1.button("📝 Create Account (Sign Up)", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()
            if nav_col2.button("❓ Forgot Password?", use_container_width=True):
                st.session_state.auth_mode = "forgot"
                st.rerun()

        # ----------------- VIEW 2: SIGN UP -----------------
        elif st.session_state.auth_mode == "signup":
            st.markdown("### 📝 Register New Account")
            st.caption("Create a new authorized ShellSathi operator profile.")

            reg_name = st.text_input("👤 Full Name:", placeholder="e.g. Harsh Vilas Aher")
            reg_email = st.text_input("📧 Email Address:", placeholder="e.g. student@pune.edu")
            reg_password = st.text_input(
                "🔒 Password (min 6 chars):",
                type=pwd_input_type,
                placeholder="Choose a strong password...",
            )
            reg_confirm = st.text_input(
                "🔁 Confirm Password:",
                type=pwd_input_type,
                placeholder="Re-type your password...",
            )

            if st.button(
                "🚀 Register & Activate Account", type="primary", use_container_width=True
            ):
                if reg_password != reg_confirm:
                    st.error("❌ Passwords do not match.")
                else:
                    ok, msg = register_user(reg_email, reg_name, reg_password)
                    if ok:
                        st.success(f"✅ {msg}")
                        user, _ = authenticate_user(reg_email, reg_password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.rerun()
                    else:
                        st.error(f"❌ {msg}")

            st.markdown("---")
            if st.button("⬅️ Already have an account? Back to Login", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

        # ----------------- VIEW 3: FORGOT PASSWORD -----------------
        elif st.session_state.auth_mode == "forgot":
            st.markdown("### 🔑 Reset Account Password")
            st.caption("Provide your registered email to establish a new password.")

            reset_email = st.text_input(
                "📧 Registered Email Address:", placeholder="e.g. harsh@shellsathi.com"
            )
            reset_pwd1 = st.text_input(
                "🔒 New Password (min 6 chars):",
                type=pwd_input_type,
                placeholder="Enter new password...",
            )
            reset_pwd2 = st.text_input(
                "🔁 Confirm New Password:",
                type=pwd_input_type,
                placeholder="Re-type new password...",
            )

            if st.button("🔄 Update Password", type="primary", use_container_width=True):
                if reset_pwd1 != reset_pwd2:
                    st.error("❌ Passwords do not match.")
                else:
                    ok, msg = reset_password(reset_email, reset_pwd1)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

            st.markdown("---")
            if st.button("⬅️ Back to Login", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

    # Block access to the rest of the application until authenticated
    st.stop()


# ------------------------------------------------------------------------------
# 5. Main Dashboard (Strictly Required Sections Only)
# ------------------------------------------------------------------------------
with st.sidebar:
    # Section A: Project Header & Tagline
    st.markdown("## 🐧 ShellSathi")
    st.caption("Intelligent Linux Command Assistant (SJ-62)")

    # Section B: Operating Mode
    st.markdown("---")
    st.markdown("### ⚙️ Operating Mode")
    mode = st.radio(
        "Select Assistant Mode:",
        options=["Ask (RAG Retrieval)", "Agent (LangGraph Agent)"],
        index=0,
        help="Ask mode retrieves verified documentation chunks. Agent mode uses tools, chmod calculator, and human approvals.",
    )

    top_k = 3
    if mode.startswith("Ask"):
        top_k = st.slider("Retrieval Context Chunks (Top-K):", min_value=1, max_value=8, value=3)

    # Section C: Backend Connection
    st.markdown("---")
    st.markdown("### 🔌 Backend Connection")
    backend_input = st.text_input(
        "FastAPI Server URL:",
        value=get_backend_url(),
        help="URL of the running ShellSathi FastAPI backend",
    )
    st.session_state.backend_url = backend_input.rstrip("/")

    start_keep_alive_pinger(st.session_state.backend_url)

    health_info = check_backend_health(st.session_state.backend_url)
    is_local = any(
        h in st.session_state.backend_url for h in ("localhost", "127.0.0.1", "api:8000")
    )

    if health_info["online"]:
        chunks = health_info["data"].get("indexed_chunks", "N/A")
        st.success(f"● Backend Online (ChromaDB: {chunks} chunks)")
    elif health_info.get("is_cold_start"):
        st.warning(
            "⏳ **Cloud Backend is Waking Up...**\n\n"
            "Render Free Tier Web Services spin down after 15 minutes of inactivity. "
            "The container is booting up (usually takes ~25–40 seconds). Please wait."
        )
        col1, col2 = st.columns(2)
        if col1.button("⚡ Auto-Wait & Reconnect", use_container_width=True):
            with st.spinner("Connecting to Render backend... please wait ~20 seconds..."):
                for _ in range(8):
                    time.sleep(4)
                    h = check_backend_health(st.session_state.backend_url, timeout=12.0)
                    if h["online"]:
                        st.rerun()
            st.rerun()
        if col2.button("🔄 Retry Connection", use_container_width=True):
            st.rerun()
    else:
        st.error(f"● Backend Offline\n\n{health_info.get('error', 'Service unavailable')}")
        if st.button("🔄 Retry Connection", use_container_width=True):
            st.rerun()
        if is_local:
            st.info("Start local backend with:\n`uvicorn app.main:app --port 8000`")
        else:
            st.info("Verify your backend deployment in the Render Dashboard.")

    # Section D: Chat Management & Logout
    st.markdown("---")
    st.markdown("### 💬 Chat Management")
    st.caption(f"Session Thread ID: `{st.session_state.thread_id}`")
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = f"user_{uuid.uuid4().hex[:8]}"
        st.session_state.feedback_status = {}
        st.session_state.pending_approval = None
        st.rerun()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

    # Section E: Project Info
    st.markdown("---")
    st.markdown("### 👤 Project Info")
    st.markdown("**Student:** Harsh Vilas Aher")
    st.markdown("**Roll Number:** 2125PCAM1004")
    st.markdown("**Project ID:** SJ-62")
    st.markdown("**Version:** Day 10 (Checkpoint 2)")


# ------------------------------------------------------------------------------
# 6. Main Terminal Canvas
# ------------------------------------------------------------------------------
st.title("🐧 ShellSathi – Intelligent Linux Command Assistant")
st.caption("SJ-62 | Day 14 Final Submission")

current_user = st.session_state.get("user") or {}
user_display_name = current_user.get("full_name", "Operator")
user_email = current_user.get("email", "operator@shellsathi.com")

st.markdown(
    f"""
    <div class="user-badge">
        👤 <strong>Authenticated Operator:</strong> <code>{user_display_name}</code> ({user_email}) &nbsp;|&nbsp;
        <span style="color: #00ff66;">● Terminal Session Active</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Render Chat History
for msg_idx, message in enumerate(st.session_state.messages):
    role = message.get("role", "assistant")
    with st.chat_message(role):
        st.markdown(message.get("content", ""))

        if role == "assistant":
            tool_used = message.get("tool_used")
            if tool_used and tool_used != "none":
                st.info(f"🔧 **Tool executed:** `{tool_used}`")

            render_citations(message.get("sources", []))

            templates = message.get("templates", [])
            if not templates and has_placeholders(message.get("content", "")):
                templates = find_command_templates(message.get("content", ""))

            for t_idx, tmpl in enumerate(templates):
                render_placeholder_filler(tmpl, f"hist_{msg_idx}_{t_idx}")

            msg_id = message.get("id", f"msg_{msg_idx}")
            current_feedback = st.session_state.feedback_status.get(msg_id)

            if current_feedback:
                rating_label = "Helpful 👍" if current_feedback == "helpful" else "Not Helpful 👎"
                st.caption(f"✅ Thank you! Rated as **{rating_label}**")
            else:
                col1, col2, _ = st.columns([1, 1, 8])
                if col1.button("👍 Helpful", key=f"thumb_up_{msg_id}"):
                    submit_feedback_api(
                        st.session_state.backend_url,
                        question=message.get("question", "General inquiry"),
                        answer=message.get("content", ""),
                        rating="helpful",
                        thread_id=st.session_state.thread_id,
                    )
                    st.session_state.feedback_status[msg_id] = "helpful"
                    st.rerun()

                if col2.button("👎 Not Helpful", key=f"thumb_down_{msg_id}"):
                    submit_feedback_api(
                        st.session_state.backend_url,
                        question=message.get("question", "General inquiry"),
                        answer=message.get("content", ""),
                        rating="not_helpful",
                        thread_id=st.session_state.thread_id,
                    )
                    st.session_state.feedback_status[msg_id] = "not_helpful"
                    st.rerun()


# Agent Human-in-the-Loop Approval Banner
if st.session_state.pending_approval:
    pending = st.session_state.pending_approval
    st.warning(
        "⚠️ **Human Authorization Required:** The ShellSathi agent has requested your approval to proceed."
    )
    st.markdown(f"**Action proposed:** {pending.get('action_summary', 'Execute agent tool')}")

    col_appr, col_rej, _ = st.columns([1.5, 1.5, 7])
    if col_appr.button("✅ Approve Action", type="primary", use_container_width=True):
        with st.spinner("Executing approved action..."):
            try:
                res = send_agent_request(
                    st.session_state.backend_url,
                    approved=True,
                    thread_id=st.session_state.thread_id,
                )
                st.session_state.pending_approval = None
                new_msg = {
                    "id": f"msg_{len(st.session_state.messages)}",
                    "role": "assistant",
                    "content": res.get("answer", "Action completed."),
                    "tool_used": res.get("tool_used", "none"),
                    "sources": res.get("sources", []),
                    "mode": "agent",
                    "question": pending.get("question", ""),
                    "templates": find_command_templates(res.get("answer", "")),
                }
                st.session_state.messages.append(new_msg)
                st.rerun()
            except Exception as exc:
                st.error(f"Error resuming agent: {exc}")

    if col_rej.button("❌ Reject Action", use_container_width=True):
        with st.spinner("Submitting rejection..."):
            try:
                res = send_agent_request(
                    st.session_state.backend_url,
                    approved=False,
                    thread_id=st.session_state.thread_id,
                )
                st.session_state.pending_approval = None
                new_msg = {
                    "id": f"msg_{len(st.session_state.messages)}",
                    "role": "assistant",
                    "content": res.get("answer", "Action cancelled by user."),
                    "tool_used": res.get("tool_used", "none"),
                    "sources": [],
                    "mode": "agent",
                    "question": pending.get("question", ""),
                }
                st.session_state.messages.append(new_msg)
                st.rerun()
            except Exception as exc:
                st.error(f"Error submitting rejection: {exc}")


# Interactive Chat Input
chat_input_val = st.chat_input(
    "Ask a Linux command question (e.g. 'find all Python files', 'chmod 755 to symbolic')..."
)
user_prompt = chat_input_val or st.session_state.pop("quick_prompt", None)

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        backend_url = st.session_state.backend_url

        if mode.startswith("Ask"):
            with st.spinner("Retrieving verified Linux documentation & generating answer..."):
                try:
                    rag_data = send_ask_request(backend_url, user_prompt, top_k=top_k)
                    answer_text = rag_data.get("answer", "")
                    sources = rag_data.get("sources", [])
                    templates = find_command_templates(answer_text)

                    st.markdown(answer_text)
                    render_citations(sources)

                    msg_key_id = f"msg_{len(st.session_state.messages)}"
                    for t_idx, tmpl in enumerate(templates):
                        render_placeholder_filler(
                            tmpl, f"new_{len(st.session_state.messages)}_{t_idx}"
                        )

                    st.session_state.messages.append(
                        {
                            "id": msg_key_id,
                            "role": "assistant",
                            "content": answer_text,
                            "sources": sources,
                            "mode": "ask",
                            "question": user_prompt,
                            "templates": templates,
                        }
                    )

                except requests.exceptions.ConnectionError:
                    err_msg = f"⚠️ Could not connect to backend at `{backend_url}`. Please verify FastAPI is running."
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
                except Exception as exc:
                    err_msg = f"Error from RAG backend: {exc}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})

        else:
            with st.spinner("ShellSathi Agent analyzing intent and executing tools..."):
                try:
                    agent_data = send_agent_request(
                        backend_url,
                        question=user_prompt,
                        thread_id=st.session_state.thread_id,
                    )
                    answer_text = agent_data.get("answer", "")
                    tool_used = agent_data.get("tool_used", "none")
                    approval_req = agent_data.get("approval_required", False)
                    sources = agent_data.get("sources", [])
                    templates = find_command_templates(answer_text)

                    st.markdown(answer_text)

                    if tool_used and tool_used != "none":
                        st.info(f"🔧 **Tool executed:** `{tool_used}`")

                    render_citations(sources)

                    msg_key_id = f"msg_{len(st.session_state.messages)}"

                    if approval_req:
                        st.session_state.pending_approval = {
                            "action_summary": answer_text,
                            "question": user_prompt,
                        }
                        st.session_state.messages.append(
                            {
                                "id": msg_key_id,
                                "role": "assistant",
                                "content": answer_text,
                                "tool_used": tool_used,
                                "approval_required": True,
                                "sources": sources,
                                "mode": "agent",
                                "question": user_prompt,
                                "templates": templates,
                            }
                        )
                        st.rerun()
                    else:
                        for t_idx, tmpl in enumerate(templates):
                            render_placeholder_filler(
                                tmpl, f"new_{len(st.session_state.messages)}_{t_idx}"
                            )

                        st.session_state.messages.append(
                            {
                                "id": msg_key_id,
                                "role": "assistant",
                                "content": answer_text,
                                "tool_used": tool_used,
                                "approval_required": False,
                                "sources": sources,
                                "mode": "agent",
                                "question": user_prompt,
                                "templates": templates,
                            }
                        )

                except requests.exceptions.ConnectionError:
                    err_msg = f"⚠️ Could not connect to backend at `{backend_url}`. Please verify FastAPI is running."
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
                except Exception as exc:
                    err_msg = f"Error from Agent backend: {exc}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
