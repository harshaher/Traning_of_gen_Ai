 # ShellSathi

 Your Smart Linux Command Assistant

One Platform. Understand Linux Commands Easily.

Project Card

- Product: ShellSathi is a beginner-friendly Linux command assistant.
- User: Students, beginners, and developers learning Linux.
- Problem: Beginners often struggle to remember Linux commands and understand how to use them.
- Solution: ShellSathi provides simple explanations, practical examples, and intelligent command search.
- Data Source: Linux command documentation and tldr-pages.

 Features

- Linux command information
- Simple command explanations
- Practical command examples
- Interactive command-line menu
- Fetch Linux command documentation
- Parse Markdown files into JSON records
- FastAPI REST API
- Smart Search using TF-IDF
- Cosine Similarity ranking
- Pandas-based data analysis
- Interactive API documentation using Swagger UI

 Technology Stack

- Python
- FastAPI
- Uvicorn
- Pandas
- Scikit-learn
- TF-IDF
- Cosine Similarity
- Requests
- JSON
- Git and GitHub

 Project Structure

Day2/
|
|-- app/
|   |-- cli.py
|   |-- fetch.py
|   |-- ingest.py
|   |-- models.py
|   |-- records.py
|   |-- smart_search.py
|   `-- main.py
|
|-- data/
|   |-- raw/
|   |-- records.json
|   `-- sample_records.py
|
|-- analysis/
|   `-- explore.py
|
|-- requirements.txt
`-- README.md

 Installation

 1. Clone the Repository

```bash
git clone https://github.com/harshaher/Traning_of_gen_Ai.git
```

 2. Open the Project Folder

```bash
cd Traning_of_gen_Ai/Day2
```

 3. Create Virtual Environment

```bash
python -m venv .venv
```

 4. Activate Virtual Environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

 5. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

 Run ShellSathi API

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Open API documentation in your browser:

```text
http://127.0.0.1:8000/docs
```

 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API status |
| GET | `/records` | Get Linux command records |
| GET | `/records/{record_id}` | Get record by ID |
| GET | `/search?q=files` | Search Linux commands |
| POST | `/questions` | Ask ShellSathi a question |

 Smart Search

ShellSathi uses the following techniques:

- TF-IDF (Term Frequency-Inverse Document Frequency)
- Cosine Similarity

These techniques rank Linux command records according to their relevance to the user's search query.

 Example Question

```json
{
  "question": "How to list files in Linux?"
}
```

ShellSathi returns relevant Linux commands such as `ls`.

 Data Analysis

Run the analysis:

```bash
python -m analysis.explore
```

 Current Dataset Summary

- Total Records: 24
- Unique Commands: 3
- Platform: Linux
- Most Common Command: grep

 Developer

Harsh Vilas Aher

MCA Student, Sanjivani University

GitHub: [harshaher](https://github.com/harshaher)

 Project Status

Week 1 - Completed

- Day 1: Project Introduction and CLI Menu
- Day 2: Linux Command Records and CLI Functions
- Day 3: Fetching and Ingesting TLDR Data
- Day 4: FastAPI, Smart Search and Pandas Analysis