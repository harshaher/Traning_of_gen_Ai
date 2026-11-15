import os
import json
from pathlib import Path
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_DIR / ".env")

QUESTIONS = [
    "How can I list files in Linux?",
    "How can I search for a pattern inside files?",
    "How can I display hidden files?",
    "How can I search for an exact string in a file?",
    "How can I list files in long format?",
    "What will the weather be tomorrow?",
    "How can I search inside files recursively?",
    "How can I create a compressed archive?",
    "How can I extract an archive into a target directory?",
    "How can I list the contents of a tar archive?",
]


def run_offline_checks():
    print("=" * 60)
    print("ShellSathi Day 6 - Prompt & LLM Offline Validation")
    print("=" * 60)

    prompt_file = PROJECT_DIR / "prompts" / "system_prompt.txt"
    if not prompt_file.exists():
        print("[FAIL] system_prompt.txt missing!")
        return False
    print("[PASS] system_prompt.txt exists and is readable.")

    for i in (1, 2):
        task_file = PROJECT_DIR / "prompts" / f"task_prompt_{i}.txt"
        if not task_file.exists():
            print(f"[FAIL] task_prompt_{i}.txt missing!")
            return False
        print(f"[PASS] task_prompt_{i}.txt exists and is readable.")

    print(f"[PASS] All {len(QUESTIONS)} benchmark questions loaded.")
    print("=" * 60)
    return True


def check_live_provider():
    groq_key = os.getenv("GROQ_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    has_groq = bool(groq_key and "your_" not in groq_key and len(groq_key) > 5)
    has_gemini = bool(gemini_key and "your_" not in gemini_key and len(gemini_key) > 5)

    if not has_groq and not has_gemini:
        print("[INFO] Live API keys are not configured in Day6/.env.")
        print("[INFO] Offline validation complete. Live testing is pending API key configuration.")
        return False

    print(f"[INFO] Live key detected (Groq: {has_groq}, Gemini: {has_gemini}).")
    return True


def main():
    if not run_offline_checks():
        return
    check_live_provider()


if __name__ == "__main__":
    main()
