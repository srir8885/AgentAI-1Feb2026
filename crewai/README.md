# CrewAI Code Creation and Review Agent

A multi-agent workflow using [CrewAI](https://docs.crewai.com/) that automatically writes Python code from natural language requirements and reviews it for quality.

## Overview

This project defines a two-agent crew:

- **Python Developer** (`coder`) — writes clean, documented Python code based on a requirement and saves it to disk.
- **Python Code Reviewer** (`reviewer`) — analyses the generated code using static analysis tools and produces a structured review report.

## Agents & Tools

### Coder Agent
- **LLM**: `gpt-4o`
- **Tool**: `FileStoreTool` — saves the generated source file to the `output/` directory.

### Reviewer Agent
- **LLM**: `gpt-4o`
- **Tools**:
  - `SyntaxCheckerTool` — parses the code with Python's `ast` module and reports any `SyntaxError`.
  - `ComplexityCheckerTool` — walks the AST to list all functions and classes, flagging any function longer than 20 lines as a refactoring candidate.

## Workflow

```
requirements (str)
      │
      ▼
 write_task  ──► Coder writes code + saves output/solution.py
      │
      ▼
review_task  ──► Reviewer runs syntax & complexity checks,
                 then outputs a structured markdown report
```

## Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**

   Create a `.env` file in this directory with your OpenAI API key:

   ```
   OPENAI_API_KEY=sk-...
   ```

## Usage

Run the crew with the default Fibonacci requirement:

```bash
python agent.py
```

To use a custom requirement, edit the `requirements` variable in the `if __name__ == "__main__":` block at the bottom of [agent.py](agent.py):

```python
requirements = "Write a function `my_func(...)` that ..."
```

The coder will save the generated code to `output/solution.py`. The reviewer's markdown report is printed to stdout at the end.

## Review Report Format

The reviewer produces a structured markdown document with the following sections:

| Section | Description |
|---|---|
| **BUGS / ERRORS** | Any syntax or logic issues found |
| **EDGE CASES** | Inputs or scenarios not handled |
| **READABILITY & STYLE** | PEP 8 and clarity notes |
| **SUGGESTED IMPROVEMENTS** | Refactoring ideas with code snippets |
| **OVERALL SCORE** | Score out of 10 |

## Project Structure

```
crewai/
├── agent.py          # Agent, tool, and crew definitions
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── output/           # Generated code is saved here (created at runtime)
```
