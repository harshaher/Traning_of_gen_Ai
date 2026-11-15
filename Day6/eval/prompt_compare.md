# ShellSathi - Prompt Comparison Evaluation

## 1. Objective
Compare two prompt versions using the ten standard ShellSathi benchmark questions to evaluate response quality, command accuracy, relevance, safety awareness, and strict JSON formatting.

## 2. Prompt Versions

### Prompt Version A (Baseline Simple Prompt)
A basic assistant instruction without strict schema enforcement or safety constraints:
```text
You are a Linux assistant. Answer the user's question with the appropriate Linux command, a short explanation, and an example.
```

### Prompt Version B (Improved ShellSathi System Prompt)
The full production system prompt defined in `prompts/system_prompt.txt` combined with task templates `prompts/task_prompt_1.txt` and `prompts/task_prompt_2.txt`:
- Explicit role and target audience (Linux beginners, students).
- Clear behavioral responsibilities (accurate syntax, practical examples, safety warnings on destructive commands).
- Explicit rule to decline out-of-scope/non-Linux queries with an honest "I don't know".
- Strict JSON output structure (`answer`, `confidence`, `follow_up`).

## 3. Evaluation Criteria
1. **Command Accuracy**: Recommends the correct Linux command and valid syntax.
2. **Clarity**: Explanations are simple and beginner-friendly.
3. **Practical Example**: Provides a realistic, runnable command example.
4. **Safety Awareness**: Highlights destructive commands (e.g. `rm`, overwrites) and prevents accidents.
5. **Out-of-Scope Handling**: Honestly declines non-Linux queries (e.g. weather) without hallucination.
6. **JSON Validity**: Conforms strictly to `{"answer": str, "confidence": float, "follow_up": str}` without markdown fences or extraneous text.

## 4. Benchmark Questions & Evaluation Results

| No. | Benchmark Question | Expected Intent | Prompt A (Baseline) | Prompt B (ShellSathi System Prompt) | Status |
|---|---|---|---|---|---|
| 1 | How can I list files in Linux? | `ls` command usage | Pending live key | Pending live key | Offline verified |
| 2 | How can I search for a pattern inside files? | `grep` command usage | Pending live key | Pending live key | Offline verified |
| 3 | How can I display hidden files? | `ls -a` flag | Pending live key | Pending live key | Offline verified |
| 4 | How can I search for an exact string in a file? | `grep -F` flag | Pending live key | Pending live key | Offline verified |
| 5 | How can I list files in long format? | `ls -l` flag | Pending live key | Pending live key | Offline verified |
| 6 | What will the weather be tomorrow? | Out of scope - honest "I don't know" | Pending live key | Pending live key | Offline verified |
| 7 | How can I search inside files recursively? | `grep -r` flag | Pending live key | Pending live key | Offline verified |
| 8 | How can I create a compressed archive? | `tar -czvf` syntax | Pending live key | Pending live key | Offline verified |
| 9 | How can I extract an archive into a target directory? | `tar -xvf -C` syntax | Pending live key | Pending live key | Offline verified |
| 10 | How can I list the contents of a tar archive? | `tar -tvf` syntax | Pending live key | Pending live key | Offline verified |

## 5. Offline Validation Summary
- **Prompt Files**: `prompts/system_prompt.txt`, `prompts/task_prompt_1.txt`, and `prompts/task_prompt_2.txt` are verified and load successfully.
- **Schema Validation**: The Pydantic `ChatResponse` model (`answer: str`, `confidence: float`, `follow_up: str`) was verified against mock responses for all 10 questions.
- **Markdown Fence Stripping**: The JSON parser in `app/main.py` strips markdown code fences (` ```json `) to ensure compatibility with various LLM response behaviors.
- **Provider Error Handling**: Verified that missing API keys gracefully return HTTP 503 with descriptive configuration error messages rather than unhandled server crashes.

## 6. Live Evaluation Status
Live API provider testing is pending configuration of a valid `GROQ_API_KEY` or `GEMINI_API_KEY` in `Day6/.env`. In accordance with project integrity rules, fake or simulated live results are not fabricated. Live testing can be executed immediately once keys are added using `python -m eval.run_eval`.
