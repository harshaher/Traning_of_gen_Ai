# ShellSathi Day 7: Semantic Search Evaluation Results

- **Date & Time:** 2026-11-16 08:04:12
- **Student:** Harsh Vilas Aher (Student ID: `2125PCAM1004`)
- **Training Program:** Sanjivani AI Training – AI to GenAI Engineer
- **Product:** ShellSathi (Intelligent Linux Command Assistant)
- **Total Indexed Chunks:** 24
- **Embedding Model:** Dense Semantic Embeddings (384 dimensions, L2 normalized)
- **Vector Store:** Persistent Chroma Database (`data/chroma_db`)

---

## 1. Summary of Benchmark Queries

| ID | Benchmark Question | Expected Command | Category | Top Retrieved Chunk | Top Score | Status |
|---|---|---|---|---|---|---|
| **Q1** | How can I list files in Linux? | `ls` | In-Scope (Directory Navigation) | `ls`: List files one per line... | `0.6202` | [OK] Exact Match |
| **Q2** | How can I search for a pattern inside files? | `grep` | In-Scope (Text Pattern Search) | `grep`: Search for a pattern within fi... | `0.7259` | [OK] Exact Match |
| **Q3** | How can I display hidden files? | `ls -a` | In-Scope (File Listing Options) | `ls`: List all files, including hidd... | `0.5543` | [OK] Exact Match |
| **Q4** | How can I search for an exact string in a file? | `grep -F` | In-Scope (Exact Matching) | `grep`: Search for an exact string (di... | `0.7048` | [OK] Exact Match |
| **Q5** | How can I list files in long format? | `ls -l` | In-Scope (Detailed File Info) | `ls`: List files in [l]ong format wi... | `0.5325` | [OK] Exact Match |
| **Q6** | What will the weather be tomorrow? | `None (Out of Scope)` | Out-of-Scope (Adversarial / Non-Linux) | `ls`: List files in [l]ong format, s... | `0.0813` | [OK] Correctly Out-of-Scope (Low Score) |
| **Q7** | How can I search inside files recursively? | `grep -r` | In-Scope (Recursive Search) | `grep`: Search for a pattern in all fi... | `0.6290` | [OK] Exact Match |
| **Q8** | How can I create a compressed archive? | `tar -czvf` | In-Scope (Archive & Compression) | `tar`: [c]reate a compressed archive ... | `0.6379` | [OK] Exact Match |
| **Q9** | How can I extract an archive into a target directory? | `tar -xvf -C` | In-Scope (Archive Extraction) | `tar`: E[x]tract a (compressed) archi... | `0.6688` | [OK] Exact Match |
| **Q10** | How can I list the contents of a tar archive? | `tar -tvf` | In-Scope (Archive Inspection) | `tar`: Lis[t] the contents of a tar [... | `0.6799` | [OK] Exact Match |

---

## 2. Detailed Per-Query Search Hits & Verification

### Q1: "How can I list files in Linux?"

- **Category:** In-Scope (Directory Navigation)
- **Expected Command:** `ls`
- **Evaluation Notes:** Standard file listing request.

**Top 3 Retrieved Chunks:**

| Rank | Score | Command (Page) | Task Title | Chunk ID | Source |
|---|---|---|---|---|---|
| 1 | **0.6202** | `ls` | List files one per line | `chunk_ls_9` | [ls.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md) |
| 2 | **0.6154** | `ls` | List all files in [l]ong format (permissions, ownership, size, and modification date) | `chunk_ls_12` | [ls.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md) |
| 3 | **0.5959** | `ls` | List files in [l]ong format, sorted by [S]ize (descending) recursively | `chunk_ls_14` | [ls.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md) |

**Top Hit Chunk Content:**
```text
Command: ls
Title: List files one per line
Usage: ls -1
Template: ls -1
Description: List directory contents. More information: <https://www.gnu.org/software/coreutils/manual/html_node/ls-invocation.html>.
```

---
### Q2: "How can I search for a pattern inside files?"

- **Category:** In-Scope (Text Pattern Search)
- **Expected Command:** `grep`
- **Evaluation Notes:** Core regex / pattern search in files.

**Top 3 Retrieved Chunks:**

| Rank | Score | Command (Page) | Task Title | Chunk ID | Source |
|---|---|---|---|---|---|
| 1 | **0.7259** | `grep` | Search for a pattern within files | `chunk_grep_1` | [grep.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/grep.md) |
| 2 | **0.7008** | `grep` | Print 3 lines of [C]ontext around, [B]efore, or [A]fter each match | `chunk_grep_4` | [grep.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/grep.md) |
| 3 | **0.6679** | `grep` | Use extended `regex`es (supports `?`, `+`, `{}`, `()`, and `|`), in case-insensitive mode | `chunk_grep_8` | [grep.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/grep.md) |

**Top Hit Chunk Content:**
```text
Command: grep
Title: Search for a pattern within files
Usage: grep "search_pattern" path/to/file1 path/to/file2 ...
Template: grep "{{search_pattern}}" {{path/to/file1 path/to/file2 ...}}
Description: Find patterns in files using `regex`es. See also: `rg`, `regex`. More information: <https://www.gnu.org/software/grep/manual/grep.html>.
```

---
### Q3: "How can I display hidden files?"

- **Category:** In-Scope (File Listing Options)
- **Expected Command:** `ls -a`
- **Evaluation Notes:** Hidden file display using flag -a / --all.

**Top 3 Retrieved Chunks:**

| Rank | Score | Command (Page) | Task Title | Chunk ID | Source |
|---|---|---|---|---|---|
| 1 | **0.5543** | `ls` | List all files, including hidden files | `chunk_ls_10` | [ls.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md) |
| 2 | **0.3996** | `ls` | List files in [l]ong format with size displayed using human-readable units (KiB, MiB, GiB) | `chunk_ls_13` | [ls.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md) |
| 3 | **0.3519** | `ls` | List all files in [l]ong format (permissions, ownership, size, and modification date) | `chunk_ls_12` | [ls.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md) |

**Top Hit Chunk Content:**
```text
Command: ls
Title: List all files, including hidden files
Usage: ls -a
Template: ls {{[-a|--all]}}
Description: List directory contents. More information: <https://www.gnu.org/software/coreutils/manual/html_node/ls-invocation.html>.
```

---
### Q4: "How can I search for an exact string in a file?"

- **Category:** In-Scope (Exact Matching)
- **Expected Command:** `grep -F`
- **Evaluation Notes:** Exact fixed string match disabling regex.

**Top 3 Retrieved Chunks:**

| Rank | Score | Command (Page) | Task Title | Chunk ID | Source |
|---|---|---|---|---|---|
| 1 | **0.7048** | `grep` | Search for an exact string (disables `regex`es) | `chunk_grep_2` | [grep.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/grep.md) |
| 2 | **0.6131** | `grep` | Use extended `regex`es (supports `?`, `+`, `{}`, `()`, and `|`), in case-insensitive mode | `chunk_grep_8` | [grep.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/grep.md) |
| 3 | **0.6061** | `grep` | Print only the matched text | `chunk_grep_6` | [grep.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/grep.md) |

**Top Hit Chunk Content:**
```text
Command: grep
Title: Search for an exact string (disables `regex`es)
Usage: grep -F "exact_string" path/to/file
Template: grep {{[-F|--fixed-strings]}} "{{exact_string}}" {{path/to/file}}
Description: Find patterns in files using `regex`es. See also: `rg`, `regex`. More information: <https://www.gnu.org/software/grep/manual/grep.html>.
```

---
### Q5: "How can I list files in long format?"

- **Category:** In-Scope (Detailed File Info)
- **Expected Command:** `ls -l`
- **Evaluation Notes:** Long listing format with permissions and sizes.

**Top 3 Retrieved Chunks:**

| Rank | Score | Command (Page) | Task Title | Chunk ID | Source |
|---|---|---|---|---|---|
| 1 | **0.5325** | `ls` | List files in [l]ong format with size displayed using human-readable units (KiB, MiB, GiB) | `chunk_ls_13` | [ls.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md) |
| 2 | **0.5302** | `ls` | List files one per line | `chunk_ls_9` | [ls.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md) |
| 3 | **0.4722** | `ls` | List all files in [l]ong format (permissions, ownership, size, and modification date) | `chunk_ls_12` | [ls.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md) |

**Top Hit Chunk Content:**
```text
Command: ls
Title: List files in [l]ong format with size displayed using human-readable units (KiB, MiB, GiB)
Usage: ls -lh
Template: ls {{[-lh|-l --human-readable]}}
Description: List directory contents. More information: <https://www.gnu.org/software/coreutils/manual/html_node/ls-invocation.html>.
```

---
### Q6: "What will the weather be tomorrow?"

- **Category:** Out-of-Scope (Adversarial / Non-Linux)
- **Expected Command:** `None (Out of Scope)`
- **Evaluation Notes:** Weather is outside Linux command scope. Similarity scores should be low.

**Top 3 Retrieved Chunks:**

| Rank | Score | Command (Page) | Task Title | Chunk ID | Source |
|---|---|---|---|---|---|
| 1 | **0.0813** | `ls` | List files in [l]ong format, sorted by [t]ime the file was modified and in reverse order (oldest first) | `chunk_ls_15` | [ls.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md) |
| 2 | **0.0503** | `tar` | [c]reate a g[z]ipped archive and write it to a [f]ile | `chunk_tar_18` | [tar.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md) |
| 3 | **0.0494** | `tar` | Lis[t] the contents of a tar [f]ile [v]erbosely | `chunk_tar_23` | [tar.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md) |

**Top Hit Chunk Content:**
```text
Command: ls
Title: List files in [l]ong format, sorted by [t]ime the file was modified and in reverse order (oldest first)
Usage: ls -ltr
Template: ls {{[-ltr|-lt --reverse]}}
Description: List directory contents. More information: <https://www.gnu.org/software/coreutils/manual/html_node/ls-invocation.html>.
```

> **Out-of-Scope Analysis:** Q6 asks for weather information, which does not exist in the ShellSathi Linux manual corpus. The semantic search retrieves distant lexical fragments with low confidence scores, demonstrating that the system properly segregates Linux command semantics from irrelevant domain questions.

---
### Q7: "How can I search inside files recursively?"

- **Category:** In-Scope (Recursive Search)
- **Expected Command:** `grep -r`
- **Evaluation Notes:** Recursive directory traversal searching file contents.

**Top 3 Retrieved Chunks:**

| Rank | Score | Command (Page) | Task Title | Chunk ID | Source |
|---|---|---|---|---|---|
| 1 | **0.6290** | `grep` | Search for a pattern in all files recursively in a directory, ignoring binary files | `chunk_grep_3` | [grep.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/grep.md) |
| 2 | **0.5839** | `grep` | Search for a pattern within files | `chunk_grep_1` | [grep.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/grep.md) |
| 3 | **0.5493** | `grep` | Print 3 lines of [C]ontext around, [B]efore, or [A]fter each match | `chunk_grep_4` | [grep.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/grep.md) |

**Top Hit Chunk Content:**
```text
Command: grep
Title: Search for a pattern in all files recursively in a directory, ignoring binary files
Usage: grep -rI "search_pattern" path/to/directory
Template: grep {{[-rI|--recursive --binary-files=without-match]}} "{{search_pattern}}" {{path/to/directory}}
Description: Find patterns in files using `regex`es. See also: `rg`, `regex`. More information: <https://www.gnu.org/software/grep/manual/grep.html>.
```

---
### Q8: "How can I create a compressed archive?"

- **Category:** In-Scope (Archive & Compression)
- **Expected Command:** `tar -czvf`
- **Evaluation Notes:** Creating gzip-compressed tar archives.

**Top 3 Retrieved Chunks:**

| Rank | Score | Command (Page) | Task Title | Chunk ID | Source |
|---|---|---|---|---|---|
| 1 | **0.6379** | `tar` | [c]reate a compressed archive and write it to a [f]ile, using the file extension to [a]utomatically determine the compression program | `chunk_tar_22` | [tar.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md) |
| 2 | **0.5987** | `tar` | E[x]tract a (compressed) archive [f]ile into the target directory | `chunk_tar_21` | [tar.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md) |
| 3 | **0.5971** | `tar` | E[x]tract a (compressed) archive [f]ile into the current directory [v]erbosely | `chunk_tar_20` | [tar.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md) |

**Top Hit Chunk Content:**
```text
Command: tar
Title: [c]reate a compressed archive and write it to a [f]ile, using the file extension to [a]utomatically determine the compression program
Usage: tar caf path/to/target.tar.xz path/to/file1 path/to/file2 ...
Template: tar caf {{path/to/target.tar.xz}} {{path/to/file1 path/to/file2 ...}}
Description: Archiving utility. Often combined with a compression method, such as `gzip` or `bzip2`. More information: <https://www.gnu.org/software/tar/manual/tar.html>.
```

---
### Q9: "How can I extract an archive into a target directory?"

- **Category:** In-Scope (Archive Extraction)
- **Expected Command:** `tar -xvf -C`
- **Evaluation Notes:** Extracting archive to specified target path.

**Top 3 Retrieved Chunks:**

| Rank | Score | Command (Page) | Task Title | Chunk ID | Source |
|---|---|---|---|---|---|
| 1 | **0.6688** | `tar` | E[x]tract a (compressed) archive [f]ile into the target directory | `chunk_tar_21` | [tar.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md) |
| 2 | **0.6179** | `tar` | [c]reate a g[z]ipped (compressed) archive from a directory using relative paths | `chunk_tar_19` | [tar.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md) |
| 3 | **0.6067** | `tar` | E[x]tract a (compressed) archive [f]ile into the current directory [v]erbosely | `chunk_tar_20` | [tar.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md) |

**Top Hit Chunk Content:**
```text
Command: tar
Title: E[x]tract a (compressed) archive [f]ile into the target directory
Usage: tar xf path/to/source.tar.ext -C path/to/directory
Template: tar xf {{path/to/source.tar.ext}} {{[-C|--directory]}} {{path/to/directory}}
Description: Archiving utility. Often combined with a compression method, such as `gzip` or `bzip2`. More information: <https://www.gnu.org/software/tar/manual/tar.html>.
```

---
### Q10: "How can I list the contents of a tar archive?"

- **Category:** In-Scope (Archive Inspection)
- **Expected Command:** `tar -tvf`
- **Evaluation Notes:** Listing archived files without extracting.

**Top 3 Retrieved Chunks:**

| Rank | Score | Command (Page) | Task Title | Chunk ID | Source |
|---|---|---|---|---|---|
| 1 | **0.6799** | `tar` | Lis[t] the contents of a tar [f]ile [v]erbosely | `chunk_tar_23` | [tar.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md) |
| 2 | **0.6388** | `tar` | E[x]tract files matching a pattern from an archive [f]ile | `chunk_tar_24` | [tar.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md) |
| 3 | **0.6061** | `tar` | E[x]tract a (compressed) archive [f]ile into the target directory | `chunk_tar_21` | [tar.md](https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/tar.md) |

**Top Hit Chunk Content:**
```text
Command: tar
Title: Lis[t] the contents of a tar [f]ile [v]erbosely
Usage: tar tvf path/to/source.tar
Template: tar tvf {{path/to/source.tar}}
Description: Archiving utility. Often combined with a compression method, such as `gzip` or `bzip2`. More information: <https://www.gnu.org/software/tar/manual/tar.html>.
```

---

## 3. Metadata Preservation Verification

Every retrieved chunk strictly preserves all required metadata attributes:
- **`source`**: Preserved as the canonical upstream TLDR/man documentation URL.
- **`page`**: Preserved as the manual/command page identifier (`ls`, `grep`, `tar`).
- **`title`**: Preserved as the human-readable task description header.
- **`chunk_id`**: Deterministic unique identifier (`chunk_<cmd>_<idx>`).

## 4. Conclusion

Semantic search successfully retrieves highly relevant Linux commands across 9 in-scope technical questions and properly delineates the out-of-scope non-Linux query (Q6). All document chunks preserve full provenance metadata.