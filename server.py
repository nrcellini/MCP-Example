"""MCP calculator server (stdio). One tool: `calculate`, one resource: TypeScript SDK README,
and prompts for guided calculator use and MCP SDK orientation.

Run:
    uv run python server.py

Develop / inspect:
    uv run mcp dev server.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ResourceError

mcp = FastMCP("Calculator")

_DOCS = Path(__file__).resolve().parent / "docs"
_TYPESCRIPT_SDK_README = _DOCS / "mcp-typescript-sdk-readme.md"
_TYPESCRIPT_SDK_README_URI = "mcp-example://docs/mcp-typescript-sdk/readme"

_TEMPLATES = Path(__file__).resolve().parent / "templates"
_MEETING_SUMMARY_TEMPLATE = _TEMPLATES / "Prompt.md"

Operation = Literal["add", "subtract", "multiply", "divide"]


@mcp.resource(
    _TYPESCRIPT_SDK_README_URI,
    name="mcp_typescript_sdk_readme",
    title="MCP TypeScript SDK README",
    description=(
        "Markdown README from the official modelcontextprotocol/typescript-sdk repository "
        "(overview, packages, installation, and links)."
    ),
    mime_type="text/markdown",
)
def mcp_typescript_sdk_readme() -> str:
    """Serve the bundled MCP TypeScript SDK README as a read-only resource."""
    if not _TYPESCRIPT_SDK_README.is_file():
        raise ResourceError(
            f"Missing documentation file: {_TYPESCRIPT_SDK_README}. "
            "Restore docs/mcp-typescript-sdk-readme.md in the project."
        )
    return _TYPESCRIPT_SDK_README.read_text(encoding="utf-8")


@mcp.tool()
def calculate(operation: Operation, a: float, b: float) -> float:
    """Perform one basic arithmetic operation on two numbers.

    Args:
        operation: One of add, subtract, multiply, divide.
        a: First operand.
        b: Second operand (divisor for divide).

    Returns:
        The result of applying the operation to a and b.
    """
    if operation == "add":
        return a + b
    if operation == "subtract":
        return a - b
    if operation == "multiply":
        return a * b
    if operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    raise ValueError(f"Unsupported operation: {operation}")


@mcp.prompt(
    name="meeting_summary",
    description=(
        "Generates an executive meeting-summary prompt from templates/meeting-summary.md. "
        "Provide the meeting date, title, and full transcript to receive a structured summary "
        "covering overview, key decisions, action items, and follow-up required."
    ),
)
def meeting_summary(meeting_date: str, meeting_title: str, transcript: str) -> str:
    """Prompt that fills the meeting summary template with the supplied meeting details."""
    template = _MEETING_SUMMARY_TEMPLATE.read_text(encoding="utf-8")
    return (
        template
        .replace("{{ meeting_date }}", meeting_date)
        .replace("{{ meeting_title }}", meeting_title)
        .replace("{{ transcript }}", transcript)
    )


@mcp.prompt(
    name="calculator_guide",
    description=(
        "Returns a system prompt that instructs the assistant to use the `calculate` tool "
        "for all arithmetic, show its work step-by-step, and explain each result in plain language."
    ),
)
def calculator_guide() -> str:
    """Prompt that primes the assistant to act as a guided calculator tutor."""
    return (
        "You are a helpful calculator assistant. "
        "Always use the `calculate` tool to perform arithmetic — never compute results mentally. "
        "For each calculation: (1) state the operation you are about to perform, "
        "(2) call the tool, (3) show the returned result, and "
        "(4) explain what the result means in plain language. "
        "If the user provides a multi-step problem, break it into individual operations "
        "and call the tool once per step."
    )


@mcp.prompt(
    name="mcp_sdk_orientation",
    description=(
        "Returns a system prompt that instructs the assistant to answer questions about the "
        "MCP TypeScript SDK by first reading the bundled README resource, then citing "
        "specific sections in every answer."
    ),
)
def mcp_sdk_orientation() -> str:
    """Prompt that scopes the assistant to MCP TypeScript SDK Q&A backed by the bundled README."""
    return (
        "You are an expert on the Model Context Protocol (MCP) TypeScript SDK. "
        "Before answering any question, retrieve the resource at "
        f"'{_TYPESCRIPT_SDK_README_URI}' and use its content as your primary source. "
        "Always cite the relevant section heading when you reference information from the README. "
        "If the README does not cover the question, say so explicitly rather than guessing."
    )


@mcp.prompt(
    name="math_word_problem_solver",
    description=(
        "Accepts a free-text word problem and returns a structured prompt that instructs the "
        "assistant to parse the problem, identify each arithmetic step, solve each step with "
        "the `calculate` tool, and present a clear final answer."
    ),
)
def math_word_problem_solver(problem: str) -> str:
    """Prompt that wraps a user-supplied word problem in a structured solving scaffold."""
    return (
        "Solve the following math word problem step-by-step. "
        "For every arithmetic operation required, use the `calculate` tool. "
        "Structure your response as:\n"
        "1. **Understanding** – restate what the problem is asking.\n"
        "2. **Plan** – list the operations needed.\n"
        "3. **Solve** – carry out each operation using the tool and show the result.\n"
        "4. **Answer** – state the final answer in a complete sentence.\n\n"
        f"Problem: {problem}"
    )


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
