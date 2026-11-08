import requests
from pathlib import Path

# Raw data folder
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# TLDR Markdown URLs
URLS = {
    "tar": "https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md",
    "ls": "https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md",
    "grep": "https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/grep.md"
}


def download_file(command, url):
    try:
        print(f"Downloading {command}...")

        response = requests.get(url, timeout=15)
        response.raise_for_status()

        file_path = RAW_DIR / f"{command}.md"
        file_path.write_text(response.text, encoding="utf-8")

        print(f"Successfully downloaded: {file_path}")

    except requests.RequestException as error:
        print(f"Error downloading {command}: {error}")


def main():
    for command, url in URLS.items():
        download_file(command, url)


if __name__ == "__main__":
    main()