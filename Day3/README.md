# ShellSathi - Day 3: Data Ingestion

This module handles data fetching and data ingestion from official Linux documentation sources.

## Data Sources
- Official repository: [tldr-pages/tldr](https://github.com/tldr-pages/tldr)
- Raw pages (Common / Linux):
  - `tar`: https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md
  - `ls`: https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md
  - `grep`: https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/grep.md

## Folder Structure
```text
Day3/
├── app/
│   ├── fetch.py        # Fetches markdown from official URLs with timeout & error handling
│   ├── ingest.py       # Cleans markdown and parses into JSON records
│   ├── models.py       # Record dataclass definition
│   └── __init__.py
├── data/
│   ├── raw/            # Downloaded markdown documents (tar.md, ls.md, grep.md)
│   └── records.json    # Ingested clean JSON records
├── requirements.txt
└── README.md
```

## Record Schema
Each parsed record contains:
- `command`: Command name (e.g. `tar`)
- `platform`: Target platform (`linux`)
- `description`: Summary of what the command does
- `example_task`: Short description of the specific operation
- `example_command`: The command syntax and arguments
- `source_url`: URL of the source document

## How to Run

1. **Fetch Raw Markdown Documents:**
   ```bash
   python -m app.fetch
   ```
   This downloads the latest markdown files to `data/raw/`.

2. **Ingest and Clean Data:**
   ```bash
   python -m app.ingest
   ```
   This parses all markdown files in `data/raw/`, cleans descriptions and tasks, and writes structured records to `data/records.json`.
