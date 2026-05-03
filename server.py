"""MCP calculator server (stdio). One tool: `calculate`.

Run:
    uv run python server.py

Develop / inspect:
    uv run mcp dev server.py
"""

from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator")

Operation = Literal["add", "subtract", "multiply", "divide"]


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
