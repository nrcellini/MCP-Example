"""MCP calculator server (stdio). One tool: `calculate`, one resource: TypeScript SDK README.

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


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
