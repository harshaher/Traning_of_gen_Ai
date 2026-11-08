import re
import json
from pathlib import Path

from app.models import Record


RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/records.json")

BASE_URL = "https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common"


def clean_markdown(file_path):
    records = []

    try:
        content = file_path.read_text(encoding="utf-8")

        command = file_path.stem
        source_url = f"{BASE_URL}/{command}.md"

        description_lines = re.findall(
            r"^>\s*(.*)",
            content,
            re.MULTILINE
        )

        description = " ".join(description_lines).strip()

        examples = re.findall(
            r"^-\s*(.*?):\s*\n\s*`([^`]+)`",
            content,
            re.MULTILINE
        )

        for task, example_command in examples:
            try:
                record = Record(
                    command=command,
                    platform="linux",
                    description=description,
                    example_task=task.strip(),
                    example_command=example_command.strip(),
                    source_url=source_url
                )

                records.append(record.__dict__)

            except Exception as error:
                print(f"Skipping invalid row: {error}")

    except (OSError, UnicodeDecodeError) as error:
        print(f"Error reading {file_path}: {error}")

    return records


def main():
    all_records = []

    for file_path in RAW_DIR.glob("*.md"):
        print(f"Processing {file_path.name}")

        records = clean_markdown(file_path)
        all_records.extend(records)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(all_records, file, indent=4, ensure_ascii=False)

    print(f"\nTotal records created: {len(all_records)}")
    print(f"JSON saved at: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()