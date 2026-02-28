import ast
import os
from pathlib import Path
from pydantic import Field
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool

load_dotenv()


class SyntaxCheckerTool(BaseTool):
    name: str = "Python Syntax Checker"
    description: str = (
        "Checks a Python code snippet for syntax errors. "
        "Input: raw Python source code as a string. "
        "Returns 'OK' or the syntax error message."
    )

    def _run(self, code: str) -> str:
        try:
            ast.parse(code)
            return "Syntax OK — no syntax errors found."
        except SyntaxError as e:
            return f"SyntaxError at line {e.lineno}: {e.msg}"


class ComplexityCheckerTool(BaseTool):
    name: str = "Complexity Checker"
    description: str = (
        "Counts functions and classes in a Python code snippet and flags "
        "functions longer than 20 lines as potentially too complex. "
        "Input: raw Python source code as a string."
    )

    def _run(self, code: str) -> str:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return f"Cannot analyse — SyntaxError: {e}"

        report = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno
                end = max(
                    getattr(n, "end_lineno", start) for n in ast.walk(node)
                )
                length = end - start + 1
                flag = " ⚠️  (>20 lines — consider refactoring)" if length > 20 else ""
                report.append(f"  def {node.name}(): {length} lines{flag}")
            elif isinstance(node, ast.ClassDef):
                report.append(f"  class {node.name}")

        if not report:
            return "No functions or classes found."
        return "Structure:\n" + "\n".join(report)


class FileStoreTool(BaseTool):
    name: str = "File Store"
    description: str = (
        "Saves text content to a file on disk. "
        "Input must be a string in the format: '<filename>|<content>' "
        "where <filename> is the relative or absolute path and <content> is what to write. "
        "Returns a confirmation message or an error."
    )
    output_dir: str = Field(default="output")

    def _run(self, input: str) -> str:
        if "|" not in input:
            return "Error: input must be '<filename>|<content>'."
        filename, _, content = input.partition("|")
        filename = filename.strip()
        path = Path(self.output_dir) / filename if not Path(filename).is_absolute() else Path(filename)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"File saved: {path.resolve()}"
        except Exception as e:
            return f"Error saving file: {e}"


coder = Agent(
    role="Python Developer",
    goal="Write clean, working Python code that meets the specified requirements.",
    backstory=(
        "You are a skilled Python developer with experience in writing efficient and maintainable code. "
        "You have a strong understanding of Python syntax and best practices. "
        "Your task is to write code that meets the requirements provided by the user, while ensuring that it is free of syntax errors and has a reasonable complexity score."
    ),
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o",
    tools=[FileStoreTool()]
)

reviewer = Agent(
    role="Python Code Reviewer",
    goal="Review Python code for syntax errors and complexity issues, and provide feedback for improvement.",
    backstory=(
        "You are an experienced Python code reviewer with a keen eye for detail. "
        "You have a deep understanding of Python syntax and best practices, as well as the ability to analyze code complexity. "
        "Your task is to review the provided Python code, identify any syntax errors or complexity issues, and provide constructive feedback to help improve the code."
    ),
    verbose=True,
    allow_delegation=False,
    llm="gpt-4o",
    tools=[SyntaxCheckerTool(), ComplexityCheckerTool()]
)

def build_tasks(requirements: str) -> list[Task]:
    
    write_task = Task(
        description=(
            f"Write a Python implementation for the following requirement:\n\n"
            f"{requirements}\n\n"
            "Include a docstring, type hints, and a brief usage example at the bottom "
            "inside an `if __name__ == '__main__':` block.\n\n"
            "After writing the code, use the File Store tool to save it. "
            "Pass the input as 'solution.py|<your code here>'."
        ),
        expected_output=(
            "Complete, runnable Python source code as a plain text code block."
        ),
        agent=coder,
    )

    review_task = Task(
        description=(
            "Review the Python code produced by the developer.\n"
            "Steps:\n"
            "1. Run the Syntax Checker tool on the code.\n"
            "2. Run the Complexity Checker tool on the code.\n"
            "3. Based on tool output AND your own analysis, write a structured review:\n"
            "   - BUGS / ERRORS (if any)\n"
            "   - EDGE CASES not handled\n"
            "   - READABILITY & STYLE notes\n"
            "   - SUGGESTED IMPROVEMENTS with short code snippets where helpful\n"
            "   - OVERALL SCORE out of 10"
        ),
        expected_output=(
            "A structured markdown code-review report with sections for bugs, "
            "edge cases, style, improvements, and an overall score."
        ),
        agent=reviewer,
        context=[write_task],
    ) 

    return write_task, review_task


if __name__ == "__main__":
    load_dotenv()
    requirements = (
        "Write a function `fibonacci(n: int) -> list[int]` that returns the first `n` numbers in the Fibonacci sequence."
    )
    write_task, review_task = build_tasks(requirements)
    crew = Crew(name="Code Creation and Review Crew", tasks=[write_task, review_task])
    results = crew.kickoff()
    print("\nFinal Results:")
    print(results)