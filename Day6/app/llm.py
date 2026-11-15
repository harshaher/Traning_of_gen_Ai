import os
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


def generate_answer(question):
    """Select the configured LLM provider."""

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    system_prompt = load_system_prompt()

    if provider == "groq":
        return ask_groq(question, system_prompt)

    if provider == "gemini":
        return ask_gemini(question, system_prompt)

    raise ValueError("Unsupported LLM provider. Choose groq or gemini.")
