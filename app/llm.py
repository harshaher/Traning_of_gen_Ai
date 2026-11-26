"""
llm.py - LLM provider wrapper for ShellSathi (Groq, Gemini, and offline student mode)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests
from dotenv import load_dotenv

from app.monitoring import TokenUsage, track_tokens

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def load_prompt_file(filename: str) -> str:
    """Load text prompt template from prompts/ directory."""
    path = PROJECT_ROOT / "prompts" / filename
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


def load_system_prompt() -> str:
    return load_prompt_file("system_prompt.txt")


def load_task_prompt(task_id: int = 1) -> str:
    return load_prompt_file(f"task_prompt_{task_id}.txt")


def get_full_prompt(task_id: int = 1) -> str:
    sys_prompt = load_system_prompt()
    task_prompt = load_task_prompt(task_id)
    if task_prompt:
        return f"{sys_prompt}\n\n{task_prompt}"
    return sys_prompt


def _ask_groq_with_usage(question: str, system_prompt: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Send chat request to Groq API and capture provider token usage."""
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("Groq API key not configured in .env.")

    models_to_try = [model]
    if model != "qwen/qwen3.8-27b":
        models_to_try.append("qwen/qwen3.8-27b")

    last_error: Optional[Exception] = None
    for m in models_to_try:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": m,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question},
                    ],
                    "temperature": 0.2,
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            usage = data.get("usage")
            return data["choices"][0]["message"]["content"], usage
        except Exception as exc:
            last_error = exc
            if "model_not_found" in str(exc) or "does not exist" in str(exc):
                continue
            raise exc

    if last_error:
        raise last_error
    raise ValueError("No response from Groq.")


def ask_groq(question: str, system_prompt: str) -> str:
    """Send chat request to Groq API."""
    content, _ = _ask_groq_with_usage(question, system_prompt)
    return content


def _ask_gemini_with_usage(
    question: str, system_prompt: str
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Send chat request to Google Gemini API and capture provider token usage."""
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Gemini API key not configured in .env.")

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json={
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": question}]}],
            "generationConfig": {"temperature": 0.2},
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    usage = data.get("usageMetadata")
    return data["candidates"][0]["content"]["parts"][0]["text"], usage


def ask_gemini(question: str, system_prompt: str) -> str:
    """Send chat request to Google Gemini API."""
    content, _ = _ask_gemini_with_usage(question, system_prompt)
    return content


def generate_offline_response(question: str) -> str:
    """
    Offline response generator adhering strictly to the ShellSathi JSON schema.
    Used when API keys are absent or during offline testing.
    """
    q_lower = question.lower()

    if any(
        term in q_lower
        for term in ["vpn", "hinjewadi", "weather", "tomorrow", "rain", "stock", "cricket"]
    ):
        return json.dumps(
            {
                "answer": "I don't know. I am ShellSathi, an assistant dedicated exclusively to Linux commands. I have no access to real-time company network metrics or external live data.",
                "confidence": 0.0,
                "follow_up": "Would you like help with a standard Linux networking command like 'ip route', 'ping', or 'traceroute' instead?",
            }
        )

    if "hidden" in q_lower:
        return json.dumps(
            {
                "answer": "In Linux, hidden files begin with a dot ('.'). Run 'ls -a' or 'ls --all' to display all files including hidden ones.",
                "confidence": 0.95,
                "follow_up": "Would you like to combine this with '-l' to view file permissions and sizes with 'ls -la'?",
            }
        )

    if "exact" in q_lower:
        return json.dumps(
            {
                "answer": "Use 'grep -F' (fixed strings) to search for an exact string without regex interpretation: 'grep -F \"exact_text\" filename'.",
                "confidence": 0.95,
                "follow_up": "Do you need the search to be case-insensitive using the '-i' flag?",
            }
        )

    if "long" in q_lower:
        return json.dumps(
            {
                "answer": "Run 'ls -l' to list directory contents in long format, showing file permissions, owner, group, byte size, and last modified date.",
                "confidence": 0.95,
                "follow_up": "Would you like to display sizes in human-readable units (KB, MB, GB) using 'ls -lh'?",
            }
        )

    if "recursiv" in q_lower:
        return json.dumps(
            {
                "answer": "Run 'grep -r \"pattern\" /path/to/dir' to search all files recursively. Tip: Use 'grep -rI' to skip binary files.",
                "confidence": 0.95,
                "follow_up": "Would you like to print line numbers alongside matches using the '-n' flag?",
            }
        )

    if "create" in q_lower and ("archive" in q_lower or "tar" in q_lower or "compress" in q_lower):
        return json.dumps(
            {
                "answer": "Use 'tar -czvf archive_name.tar.gz /path/to/folder'. Flags: -c (create), -z (gzip), -v (verbose), -f (filename).",
                "confidence": 0.95,
                "follow_up": "Would you like to know how to create a bzip2 archive ('.tar.bz2') for higher compression?",
            }
        )

    if "extract" in q_lower:
        return json.dumps(
            {
                "answer": "Use 'tar -xvf archive.tar.gz -C /target/directory'. The '-C' flag changes directory before extraction.",
                "confidence": 0.95,
                "follow_up": "Make sure the target directory exists before running the command. Would you like to create it with 'mkdir -p'?",
            }
        )

    if "contents" in q_lower and ("tar" in q_lower or "archive" in q_lower):
        return json.dumps(
            {
                "answer": "Run 'tar -tvf archive.tar.gz' to list the contents without extracting. Flags: -t (list), -v (verbose), -f (file).",
                "confidence": 0.95,
                "follow_up": "Would you like to search for a specific file inside the archive using 'tar -tf archive.tar.gz | grep filename'?",
            }
        )

    if "pattern" in q_lower or "search" in q_lower:
        return json.dumps(
            {
                "answer": "Use 'grep \"pattern\" filename' to search for matching lines within a file.",
                "confidence": 0.95,
                "follow_up": "Do you want to search across all files in a directory recursively?",
            }
        )

    return json.dumps(
        {
            "answer": "Use 'ls' to list files in the current directory. For one file per line, use 'ls -1'.",
            "confidence": 0.95,
            "follow_up": "Would you like to see how to list hidden files or sort files by modification date?",
        }
    )


def generate_answer_with_usage(
    question: str, task_id: int = 1, request_id: Optional[str] = None
) -> Tuple[str, TokenUsage]:
    """Generate answer and track token usage from provider or offline estimation."""
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    full_prompt = get_full_prompt(task_id)

    model_name = (
        os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        if provider == "groq"
        else os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    )
    raw_content = ""
    actual_usage: Optional[Dict[str, Any]] = None

    try:
        if provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key or api_key == "your_groq_api_key_here":
                raw_content = generate_offline_response(question)
                model_name = "offline-heuristic-engine"
            else:
                raw_content, actual_usage = _ask_groq_with_usage(question, full_prompt)
        elif provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here":
                raw_content = generate_offline_response(question)
                model_name = "offline-heuristic-engine"
            else:
                raw_content, actual_usage = _ask_gemini_with_usage(question, full_prompt)
        else:
            raw_content = generate_offline_response(question)
            model_name = "offline-heuristic-engine"
    except Exception:
        raw_content = generate_offline_response(question)
        model_name = "offline-heuristic-engine"

    usage = track_tokens(
        model_name=model_name,
        input_text=f"{full_prompt}\n{question}",
        output_text=raw_content,
        actual_usage=actual_usage,
        request_id=request_id,
    )
    return raw_content, usage


def generate_answer(question: str, task_id: int = 1) -> str:
    """Generate answer using configured provider or offline fallback."""
    content, _ = generate_answer_with_usage(question, task_id=task_id)
    return content
