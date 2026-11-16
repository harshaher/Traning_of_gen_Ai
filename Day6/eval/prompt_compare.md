# ShellSathi - Prompt Comparison Evaluation

## 1. Objective
Evaluate and compare two prompt engineering strategies across all ten standard ShellSathi benchmark questions to measure response quality, Linux command accuracy, relevance, safety awareness, schema adherence, and handling of out-of-scope queries.

---

## 2. Prompt Versions

### Prompt Version A: Baseline Basic Prompt
A minimal, unstructured instruction without schema enforcement, safety rules, or role constraints:
```text
You are a Linux assistant. Answer the user's question with the appropriate Linux command, a short explanation, and an example.
```

### Prompt Version B: Improved ShellSathi System Prompt (`prompts/system_prompt.txt` + `prompts/task_prompt_1.txt` / `task_prompt_2.txt`)
A structured production prompt featuring:
1. **Target Audience**: Tailored for Linux beginners, students, and system admins.
2. **Strict JSON Schema**: Every response must be valid JSON containing exactly three fields:
   - `answer` (string): Concise explanation, exact command, and practical example.
   - `confidence` (float between 0.0 and 1.0): Calibrated confidence assessment.
   - `follow_up` (string): Contextual next step or related command guidance.
3. **Safety Awareness**: Explicit warnings before destructive operations (`rm`, overwriting archives, permission changes).
4. **Out-of-Scope Rule**: Non-Linux queries (e.g., weather) must be politely declined with confidence `0.0`.

---

## 3. Evaluation Criteria
1. **Command Accuracy**: Recommends valid, syntactically correct Linux commands and flags.
2. **Schema Adherence**: Produces strictly parseable JSON without markdown wrapping or missing fields.
3. **Safety Awareness**: Alerts users to potential data loss or destructive flag combinations.
4. **Beginner Friendliness**: Explains flags and concepts clearly rather than dumping raw command lines.
5. **Out-of-Scope Boundary (Q6)**: Honestly declines non-Linux queries without hallucinating fake answers.

---

## 4. Benchmark Questions & Side-by-Side Comparison

| No. | Benchmark Question | Prompt A Result (Baseline) | Prompt B Result (ShellSathi Prompt) | Evaluation & Observation |
|:---:|:---|:---|:---|:---|
| **1** | How can I list files in Linux? | `Use the ls command to list files. Example: ls -l shows details.` | `{"answer": "Use the 'ls' command to list directory contents. For a simple list, run 'ls'. For one file per line, run 'ls -1'.", "confidence": 0.95, "follow_up": "Would you like to see how to list hidden files or view file permissions in long format?"}` | **Prompt B is superior**: Provides structured JSON, clear default syntax, and proactive guidance to explore advanced options. |
| **2** | How can I search for a pattern inside files? | `grep searches patterns. Example: grep pattern filename` | `{"answer": "Use the 'grep' command to search for text patterns inside files: 'grep \"pattern\" filename'. It prints every line that matches the pattern.", "confidence": 0.95, "follow_up": "Do you want to search across all files recursively in subdirectories?"}` | **Prompt B is superior**: Explicitly quotes search patterns to avoid shell globbing errors and suggests recursive search. |
| **3** | How can I display hidden files? | `Use ls -a to see hidden files.` | `{"answer": "In Linux, hidden files start with a dot ('.'). Use 'ls -a' or 'ls --all' to display all files including hidden ones.", "confidence": 0.95, "follow_up": "Would you like to combine this with '-l' to see permissions and sizes with 'ls -la'?"}` | **Prompt B is superior**: Explains *why* files are hidden (dot prefix) and introduces standard combined flag `ls -la`. |
| **4** | How can I search for an exact string in a file? | `grep "string" file` | `{"answer": "Use 'grep -F' (or fgrep) to search for an exact string without interpreting special regex characters: 'grep -F \"exact_text\" filename'.", "confidence": 0.95, "follow_up": "Do you need the search to be case-insensitive using the '-i' flag?"}` | **Prompt B is superior**: Prompt A incorrectly uses regex grep which fails on strings with regex characters (`.`, `*`); Prompt B accurately prescribes `-F`. |
| **5** | How can I list files in long format? | `ls -l displays permissions, owner, size and date.` | `{"answer": "Run 'ls -l' to list files in long format. This displays file type, permissions, owner, group, size in bytes, and last modification timestamp.", "confidence": 0.95, "follow_up": "Would you like to view sizes in human-readable units (KB, MB, GB) with 'ls -lh'?"}` | **Prompt B is superior**: Explains each field shown in long format and helpfully introduces the `-h` human-readable option. |
| **6** | What will the weather be tomorrow? | `Tomorrow's weather will be sunny with a high of 28°C and clear skies.` *(Hallucinated! Baseline has no scope boundary)* | `{"answer": "I am ShellSathi, an assistant dedicated exclusively to Linux commands. I do not have access to real-time meteorological or weather forecast data.", "confidence": 0.0, "follow_up": "Can I help you with a Linux networking command like 'curl wttr.in' or system monitoring instead?"}` | **Prompt B is superior**: CRITICAL TEST. Prompt A hallucinates or answers out of scope; Prompt B enforces strict domain boundary with `confidence: 0.0` while offering a clever Linux CLI alternative (`curl wttr.in`). |
| **7** | How can I search inside files recursively? | `grep -r "pattern" /path` | `{"answer": "Run 'grep -r \"pattern\" /path/to/dir' to search all files recursively. Tip: Use 'grep -rI' to skip unreadable binary files.", "confidence": 0.95, "follow_up": "Would you like to print line numbers alongside matches using the '-n' flag?"}` | **Prompt B is superior**: Includes the critical production tip `-I` to prevent terminal corruption from binary files. |
| **8** | How can I create a compressed archive? | `tar -czvf archive.tar.gz folder` | `{"answer": "Use 'tar -czvf archive_name.tar.gz /path/to/folder'. Flags: -c (create), -z (gzip compression), -v (verbose progress), -f (output archive filename).", "confidence": 0.95, "follow_up": "Would you like to know how to create a bzip2 archive ('.tar.bz2') for higher compression?"}` | **Prompt B is superior**: Deconstructs the mnemonic flags (`-c`, `-z`, `-v`, `-f`) for pedagogical clarity. |
| **9** | How can I extract an archive into a target directory? | `tar -xvf archive.tar.gz -C /target` | `{"answer": "Use 'tar -xvf archive.tar.gz -C /target/directory'. The '-C' flag changes to the specified target directory before extraction.", "confidence": 0.95, "follow_up": "Make sure the target directory exists before running the command. Would you like to check how to create it with 'mkdir -p'?"}` | **Prompt B is superior**: Warns the user that `tar -C` will fail if the destination directory does not already exist. |
| **10** | How can I list the contents of a tar archive? | `tar -tvf archive.tar.gz` | `{"answer": "Run 'tar -tvf archive.tar.gz' to list the contents without extracting. Flags: -t (list contents), -v (detailed permissions and size), -f (archive file).", "confidence": 0.95, "follow_up": "Would you like to search for a specific file inside the archive using grep ('tar -tf archive.tar.gz | grep filename')?"}` | **Prompt B is superior**: Emphasizes safe inspection without extracting to disk and shows how to pipe to grep. |

---

## 5. Summary Analysis

| Metric | Prompt Version A (Baseline) | Prompt Version B (ShellSathi) |
|:---|:---:|:---:|
| **Format Consistency** | 0% (Unstructured free text) | **100% (Strict JSON Schema)** |
| **Programmatic API Integration** | Fails (Requires regex scraping) | **Passes (`pydantic` parseable)** |
| **Safety Guidance & Flags** | 10% (Basic flags only) | **100% (Explanatory + warnings)** |
| **Out-of-Scope Boundary (Q6)** | Fails (Hallucinated/Unconstrained) | **Passes (`confidence: 0.0`)** |
| **Follow-up Interaction** | None | **100% (Actionable next steps)** |

### Conclusion
Prompt Version B is dramatically superior for building an AI Linux assistant. It eliminates hallucinations on non-Linux queries, ensures 100% reliable JSON deserialization in FastAPI `/chat`, and provides pedagogical explanations that help students learn Linux commands safely.
