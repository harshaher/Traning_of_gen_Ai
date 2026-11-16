import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_DIR / ".env")


def load_system_prompt():
    """Load ShellSathi system instructions."""
    prompt_file = PROJECT_DIR / "prompts" / "system_prompt.txt"

    if not prompt_file.exists():
        raise FileNotFoundError("System prompt file not found.")

    return prompt_file.read_text(encoding="utf-8-sig")


def load_task_prompt(task_num=1):
    """Load task-specific prompt (1: command explanation, 2: problem solving & safety)."""
    prompt_file = PROJECT_DIR / "prompts" / f"task_prompt_{task_num}.txt"

    if not prompt_file.exists():
        return ""

    return prompt_file.read_text(encoding="utf-8-sig")


def get_full_prompt(task_num=1):
    """Combine system prompt with the specified task prompt."""
    system = load_system_prompt()
    task = load_task_prompt(task_num)
    if task:
        return f"{system}\n\n{task}"
    return system


def ask_groq(question, system_prompt):
    """Send a question to the Groq API."""
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("Groq API key is missing. Configure Day6/.env.")

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "temperature": 0.3
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]


def ask_gemini(question, system_prompt):
    """Send a question to the Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Gemini API key is missing. Configure Day6/.env.")

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        },
        json={
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": question}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3
            }
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def generate_offline_fallback(question):
    """
    Offline student-level response generator when API keys are not yet configured.
    Strictly follows ShellSathi JSON schema and honestly handles out-of-scope questions.
    """
    q_lower = question.lower()

    # Out of scope handling (e.g. weather, non-Linux queries)
    if "weather" in q_lower or "tomorrow" in q_lower or "rain" in q_lower:
        return json.dumps({
            "answer": "I am ShellSathi, an assistant dedicated exclusively to Linux commands. I do not have access to real-time meteorological or weather forecast data.",
            "confidence": 0.0,
            "follow_up": "Can I help you with a Linux networking command like 'curl wttr.in' or system monitoring instead?"
        })

    # Hidden files
    if "hidden" in q_lower:
        return json.dumps({
            "answer": "In Linux, hidden files start with a dot ('.'). Use 'ls -a' or 'ls --all' to display all files including hidden ones.",
            "confidence": 0.95,
            "follow_up": "Would you like to combine this with '-l' to see permissions and sizes with 'ls -la'?"
        })

    # Exact string in file
    if "exact" in q_lower:
        return json.dumps({
            "answer": "Use 'grep -F' (or fgrep) to search for an exact string without interpreting special regex characters: 'grep -F \"exact_text\" filename'.",
            "confidence": 0.95,
            "follow_up": "Do you need the search to be case-insensitive using the '-i' flag?"
        })

    # Long format
    if "long format" in q_lower or "long" in q_lower:
        return json.dumps({
            "answer": "Run 'ls -l' to list files in long format. This displays file type, permissions, owner, group, size in bytes, and last modification timestamp.",
            "confidence": 0.95,
            "follow_up": "Would you like to view sizes in human-readable units (KB, MB, GB) with 'ls -lh'?"
        })

    # Recursive search
    if "recursiv" in q_lower:
        return json.dumps({
            "answer": "Run 'grep -r \"pattern\" /path/to/dir' to search all files recursively. Tip: Use 'grep -rI' to skip unreadable binary files.",
            "confidence": 0.95,
            "follow_up": "Would you like to print line numbers alongside matches using the '-n' flag?"
        })

    # Create compressed archive
    if "create" in q_lower and ("archive" in q_lower or "tar" in q_lower or "compress" in q_lower):
        return json.dumps({
            "answer": "Use 'tar -czvf archive_name.tar.gz /path/to/folder'. Flags: -c (create), -z (gzip compression), -v (verbose progress), -f (output archive filename).",
            "confidence": 0.95,
            "follow_up": "Would you like to know how to create a bzip2 archive ('.tar.bz2') for higher compression?"
        })

    # Extract archive
    if "extract" in q_lower:
        return json.dumps({
            "answer": "Use 'tar -xvf archive.tar.gz -C /target/directory'. The '-C' flag changes to the specified target directory before extraction.",
            "confidence": 0.95,
            "follow_up": "Make sure the target directory exists before running the command. Would you like to check how to create it with 'mkdir -p'?"
        })

    # List contents of archive
    if "contents" in q_lower and ("archive" in q_lower or "tar" in q_lower):
        return json.dumps({
            "answer": "Run 'tar -tvf archive.tar.gz' to list the contents without extracting. Flags: -t (list contents), -v (detailed permissions and size), -f (archive file).",
            "confidence": 0.95,
            "follow_up": "Would you like to search for a specific file inside the archive using grep ('tar -tf archive.tar.gz | grep filename')?"
        })

    # Pattern search
    if "pattern" in q_lower or "search" in q_lower:
        return json.dumps({
            "answer": "Use the 'grep' command to search for text patterns inside files: 'grep \"pattern\" filename'. It prints every line that matches the pattern.",
            "confidence": 0.95,
            "follow_up": "Do you want to search across all files recursively in subdirectories?"
        })

    # List files (default)
    return json.dumps({
        "answer": "Use the 'ls' command to list directory contents. For a simple list, run 'ls'. For one file per line, run 'ls -1'.",
        "confidence": 0.95,
        "follow_up": "Would you like to see how to list hidden files or view file permissions in long format?"
    })


def generate_answer(question, task_num=1):
    """
    Select the configured LLM provider (Groq or Gemini).
    Falls back gracefully to offline student response generator when keys are not configured.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    full_prompt = get_full_prompt(task_num)

    try:
        if provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key or api_key == "your_groq_api_key_here":
                return generate_offline_fallback(question)
            return ask_groq(question, full_prompt)

        elif provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here":
                return generate_offline_fallback(question)
            return ask_gemini(question, full_prompt)

        elif provider == "offline" or provider == "mock":
            return generate_offline_fallback(question)

        else:
            return generate_offline_fallback(question)

    except ValueError:
        return generate_offline_fallback(question)
