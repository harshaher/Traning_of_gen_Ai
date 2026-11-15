# How LLMs Work

## 1. What is an LLM?

LLM stands for Large Language Model. It is an Artificial Intelligence model trained on a large amount of text data.

An LLM understands patterns in language and generates responses based on the input provided by a user.

Examples of LLM applications include chatbots, AI assistants, text summarization, and question-answering systems.

## 2. How Does an LLM Work?

An LLM generally works through the following steps:

1. User Input: The user enters a question or instruction.
2. Tokenization: The input text is divided into smaller units called tokens.
3. Processing: The model processes the tokens and identifies language patterns.
4. Prediction: The model predicts the next suitable token based on the previous context.
5. Response Generation: The model generates tokens to create a meaningful response.
6. Output: The final response is displayed to the user.

## 3. LLM Workflow Diagram

```text
        User Question
              |
              v
        Tokenization
              |
              v
       Model Processing
              |
              v
      Next Token Prediction
              |
              v
      Response Generation
              |
              v
        Final Answer
```

## 4. What is Prompt Engineering?

Prompt engineering means writing clear instructions or questions to get useful responses from an AI model.

Example:

Poor Prompt:
Tell me about Linux.

Better Prompt:
Explain the Linux ls command with its purpose and one practical example.

A clear prompt helps an AI model understand the user's requirements.

## 5. How Does ShellSathi Work?

ShellSathi is a beginner-friendly Linux command assistant.

It uses a JSON dataset containing Linux command information collected from tldr-pages.

Current dataset information:

- Total Records: 24
- Unique Commands: 3
- Available Commands: grep, ls, tar

ShellSathi uses TF-IDF and Cosine Similarity for intelligent command searching.

### Search Process

1. The user enters a Linux-related question.
2. ShellSathi loads command records from records.json.
3. The application combines command information, descriptions, and examples.
4. TF-IDF converts the text into numerical vectors.
5. Cosine Similarity calculates the similarity between the question and dataset records.
6. Matching records are sorted by relevance score.
7. ShellSathi returns the most relevant results.

**Important:** The current ShellSathi implementation uses TF-IDF and Cosine Similarity. It does not currently connect to an LLM API.

## 6. Ten Real ShellSathi User Questions

| No. | User Question | Expected Result |
|---|---|---|
| 1 | How can I list files in Linux? | ls |
| 2 | How can I search for a pattern inside files? | grep |
| 3 | How can I display hidden files? | ls |
| 4 | How can I search for an exact string in a file? | grep |
| 5 | How can I list files in long format? | ls |
| 6 | What will the weather be tomorrow? | Out of scope - honest "I don't know" |
| 7 | How can I search inside files recursively? | grep |
| 8 | How can I create a compressed archive? | tar |
| 9 | How can I extract an archive into a target directory? | tar |
| 10 | How can I list the contents of a tar archive? | tar |

Question 6 is outside the scope of the current Linux command dataset. ShellSathi must provide an honest "I don't know" response rather than hallucinating an answer.

## 7. FastAPI in ShellSathi

FastAPI provides REST API endpoints so other applications can communicate with ShellSathi.

Current API endpoints:

- GET /health
- GET /records
- GET /records/{record_id}
- GET /search
- POST /questions

Swagger UI provides an interactive interface for testing these endpoints.

## 8. Conclusion

Large Language Models understand and generate human language using patterns learned during training.

ShellSathi demonstrates intelligent text searching using TF-IDF and Cosine Similarity. It helps Linux beginners find relevant commands through simple natural-language questions.

In the future, an LLM can be integrated into ShellSathi to provide more conversational explanations and interactive learning support.
