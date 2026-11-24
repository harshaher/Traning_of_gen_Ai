"""
ui/app.py - ShellSathi Streamlit Web Application (Day 10)

Features:
  - Mode 1: Ask (RAG Retrieval with verified citations)
  - Mode 2: Agent (LangGraph Autonomous Agent with chmod calculator and human approval)
  - Signature Feature: Interactive Placeholder Filler for Linux commands
  - Feedback Mechanism: Thumbs Up / Thumbs Down persisted via POST /feedback
  - Thread-isolated session memory and backend health monitoring
"""

import os
import sys
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

from app.placeholder import (
    extract_placeholders,
    fill_template,
    find_command_templates,
    has_placeholders,
)

st.set_page_config(
    page_title="ShellSathi - Linux Command Assistant",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_backend_url() -> str:
    """Retrieve backend URL from session state or environment variable."""
    url = (
        st.session_state.get(
            "backend_url",
            os.environ.get("BACKEND_URL", "http://127.0.0.1:8000"),
        )
        .strip()
        .rstrip("/")
    )
    if not (url.startswith("http://") or url.startswith("https://")):
        if "127.0.0.1" in url or "localhost" in url or url.startswith("api:"):
            url = f"http://{url}"
        else:
            url = f"https://{url}"

    # Auto-resolve Render service slug: if user or Render set 'shellsathi-api' without domain
    # e.g. https://shellsathi-api -> https://shellsathi-api.onrender.com
    clean_host = url.split("://")[-1].split(":")[0]
    if "." not in clean_host and clean_host not in ("localhost", "api"):
        url = f"https://{clean_host}.onrender.com"

    return url


def check_backend_health(base_url: str, timeout: float = 10.0) -> Dict[str, Any]:
    """Query FastAPI healthcheck endpoint with automatic retry for cold starts."""
    for attempt in range(2):
        try:
            resp = requests.get(f"{base_url}/health", timeout=timeout)
            if resp.status_code == 200:
                return {"online": True, "data": resp.json()}
            if resp.status_code in (502, 503) and attempt == 0:
                time.sleep(2)
                continue
            error_msg = f"HTTP {resp.status_code}"
            if resp.status_code in (502, 503):
                error_msg += " (Backend is waking up or deploying on Render. Please click 'Recheck Connection' below.)"
            return {"online": False, "error": error_msg}
        except requests.exceptions.Timeout:
            if attempt == 0:
                continue
            return {
                "online": False,
                "error": "Connection timed out. The backend service may be waking up from sleep (Render free tier cold start). Please wait a moment and refresh.",
            }
        except Exception as exc:
            return {"online": False, "error": str(exc)}
    return {"online": False, "error": "Backend unreachable"}


def send_ask_request(base_url: str, question: str, top_k: int = 3) -> Dict[str, Any]:
    """Call POST /ask endpoint (Mode 1: RAG)."""
    url = f"{base_url}/ask"
    payload = {"question": question, "top_k": top_k}
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def send_agent_request(
    base_url: str,
    question: Optional[str] = None,
    approved: Optional[bool] = None,
    thread_id: str = "default_user",
) -> Dict[str, Any]:
    """Call POST /agent endpoint (Mode 2: LangGraph Agent)."""
    url = f"{base_url}/agent"
    payload: Dict[str, Any] = {"thread_id": thread_id}
    if question is not None:
        payload["question"] = question
    if approved is not None:
        payload["approved"] = approved
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def submit_feedback_api(
    base_url: str,
    question: str,
    answer: str,
    rating: str,
    thread_id: Optional[str] = None,
) -> bool:
    """Call POST /feedback endpoint to persist rating."""
    url = f"{base_url}/feedback"
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


if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"user_{uuid.uuid4().hex[:8]}"

if "feedback_status" not in st.session_state:
    st.session_state.feedback_status = {}

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None

if (
    "demo" in st.query_params or st.query_params.get("demo") == "1"
) and not st.session_state.messages:
    demo_ans = (
        "To extract an archive into a specific target directory, use the `tar` command with the `-C` flag:\n\n"
        "```bash\n"
        "tar -xvf {{archive.tar.gz}} -C {{target_directory}}\n"
        "```\n\n"
        "**Options explanation:**\n"
        "- `-x`: Extract files from an archive\n"
        "- `-v`: Verbosely list files processed\n"
        "- `-f`: Archive file to read\n"
        "- `-C`: Decompress files into specified target directory"
    )
    st.session_state.messages = [
        {"role": "user", "content": "How do I extract a tar archive to a specific folder?"},
        {
            "id": "msg_demo_0",
            "role": "assistant",
            "content": demo_ans,
            "sources": ["https://tldr.sh/linux/tar"],
            "mode": "ask",
            "question": "How do I extract a tar archive to a specific folder?",
            "templates": find_command_templates(demo_ans),
        },
    ]


with st.sidebar:
    st.markdown("## 🐧 ShellSathi")
    st.caption("Intelligent Linux Command Assistant")

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

    st.markdown("---")
    st.markdown("### 🔌 Backend Connection")
    backend_input = st.text_input(
        "FastAPI Server URL:",
        value=get_backend_url(),
        help="URL of the running ShellSathi FastAPI backend",
    )
    st.session_state.backend_url = backend_input.rstrip("/")

    health_info = check_backend_health(st.session_state.backend_url)
    if health_info["online"]:
        chunks = health_info["data"].get("indexed_chunks", "N/A")
        st.success(f"● Backend Online (ChromaDB: {chunks} chunks)")
    else:
        st.error(f"● Backend Offline\n{health_info.get('error', '')}")
        if st.button("🔄 Recheck Connection", use_container_width=True):
            st.rerun()
        st.info("Start backend with: `uvicorn app.main:app --port 8000`")

    st.markdown("---")
    st.markdown("### 💬 Chat Management")
    st.caption(f"Session Thread ID: `{st.session_state.thread_id}`")
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = f"user_{uuid.uuid4().hex[:8]}"
        st.session_state.feedback_status = {}
        st.session_state.pending_approval = None
        st.rerun()


st.title("🐧 ShellSathi – Your Linux Command Assistant")
st.markdown(
    "Welcome to **ShellSathi**! Ask questions about Linux commands, search documentation, "
    "convert permissions with the **chmod calculator**, and use the interactive **Placeholder Filler**."
)

if not st.session_state.messages:
    st.markdown("### 💡 Quick Starters")
    qcols = st.columns(3)
    if qcols[0].button("📦 `tar -xvf {{archive}}` (Placeholder Demo)", use_container_width=True):
        st.session_state.quick_prompt = "How do I extract a tar archive to a specific folder?"
        st.rerun()
    if qcols[1].button("🔐 `chmod 755 to symbolic` (Agent Demo)", use_container_width=True):
        st.session_state.quick_prompt = "Convert chmod 755 to symbolic"
        st.rerun()
    if qcols[2].button("🔍 `find files by extension` (RAG Demo)", use_container_width=True):
        st.session_state.quick_prompt = "How do I find all files with .log extension using find?"
        st.rerun()

st.markdown("---")


def render_placeholder_filler(template: str, widget_key_prefix: str) -> None:
    """
    Renders an interactive widget to fill Linux command placeholders (e.g. {{source}}, {{destination}}).
    """
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
                col1, col2, col3 = st.columns([1, 1, 8])
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


if st.session_state.pending_approval:
    pending = st.session_state.pending_approval
    st.warning(
        "⚠️ **Human Approval Required**\nThe ShellSathi agent has requested your authorization to proceed."
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


chat_input_val = st.chat_input("Ask a Linux question, request a command, or convert permissions...")
user_prompt = chat_input_val or st.session_state.pop("quick_prompt", None)

if user_prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

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
