# MCP calculator server (Python)

This folder contains a minimal [Model Context Protocol](https://modelcontextprotocol.io/) server built with the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk). It exposes **exactly one tool**, `calculate`, for `add`, `subtract`, `multiply`, and `divide`.

The server uses the SDK’s high-level **`FastMCP`** API (`from mcp.server.fastmcp import FastMCP`), which matches how current PyPI releases structure the ergonomic server layer. (Some upstream docs show `MCPServer` from `mcp.server.mcpserver`; that layout applies to newer SDK revisions—the published package you install with `uv add "mcp[cli]"` uses **`FastMCP`** for the same style of `@mcp.tool()` handlers.)

---

## What you will have at the end

- A **project-local virtual environment** (`.venv`) managed by **uv**
- **`mcp[cli]`** installed into that environment via **uv**
- A working **`server.py`** you can run with **`uv run`**, test with **MCP Inspector** (`mcp dev`), or attach to **Claude Desktop** / other MCP clients over **stdio**

---

## Part 1 — Install and verify Python

MCP’s Python materials assume a **modern Python 3** (for example **3.10+**). On Windows, **Python 3.14** is often a poor default today because some dependencies may not ship prebuilt wheels yet and can fall back to Rust/MSVC builds. This project declares **`requires-python = ">=3.10,<3.14"`** so installs stay on **3.10–3.13**.

### Option A — Python from python.org (good if you want a system install)

1. Download and install Python for Windows from [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/).
2. During setup, enable **“Add python.exe to PATH”** (wording may vary slightly by installer version).
3. **Close and reopen** your terminal (PowerShell or Windows Terminal).
4. Verify:

   ```powershell
   py -0p
   ```

   You should see one or more installed Python paths.

5. Verify a concrete version (example using the launcher):

   ```powershell
   py -3.12 --version
   ```

   Example expected output shape:

   ```text
   Python 3.12.x
   ```

   If `py -3.12` is not installed yet, try `py --version` and use whatever 3.10–3.13 build you have, or use Option B.

### Option B — Let uv install a pinned Python (recommended for this repo)

From your project folder:

```powershell
uv python install 3.12
```

Verify uv sees it:

```powershell
uv python find 3.12
```

You should get a path to a `python.exe` (uv’s managed install).

---

## Part 2 — Install and verify uv

Install **uv** using the official Windows install command from the MCP documentation:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Close and reopen** your terminal so `uv` is on your `PATH`.

Verify:

```powershell
uv --version
```

Example expected output shape:

```text
uv x.y.z (...)
```

---

## Part 3 — Project folder (you already created and opened it)

These steps assume you are **already inside** your project directory (the folder that contains `server.py` and `pyproject.toml`).

Confirm:

```powershell
Get-Location
dir
```

You should see at least `pyproject.toml`, `server.py`, and this `README.md`.

---

## Part 4 — Virtual environment with uv

uv will create and use **`.venv`** in the project root.

### Pin Python (strongly recommended)

This repo is tested with **Python 3.12** via uv:

```powershell
uv python pin 3.12
```

That creates/updates **`.python-version`** so `uv` consistently picks 3.12 for this folder.

Verify the pin:

```powershell
Get-Content .python-version
```

Expected:

```text
3.12
```

### Create the venv and install dependencies

```powershell
uv sync
```

What this does:

- Creates **`.venv`** if needed
- Installs **`mcp[cli]`** and its dependencies **into `.venv`**

Verify the environment exists:

```powershell
Test-Path .\.venv\Scripts\python.exe
```

Expected: `True`

### (Optional) Activate the venv in your shell

uv does **not** require activation because `uv run ...` uses `.venv` automatically, but activation is useful for interactive work:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify:

```powershell
python --version
where.exe python
```

You should see a **3.12.x** (or other 3.10–3.13) interpreter path **inside** `.venv`.

Deactivate when finished:

```powershell
deactivate
```

---

## Part 5 — Verify `mcp` and the CLI

Run Python **through uv** so you definitely use `.venv`:

```powershell
uv run python -c "import mcp; print('mcp', mcp.__version__)"
```

You should see a version line with **no import error**.

Verify the **`mcp` CLI** entry point shipped with `mcp[cli]`:

```powershell
uv run mcp --help
```

You should see help text for the `mcp` command (including subcommands like tooling for development workflows, depending on your installed version).

---

## Part 6 — What the server implements

File: **`server.py`**

- **`calculate(operation, a, b)`** — one MCP tool
  - **`operation`**: `"add" | "subtract" | "multiply" | "divide"`
  - **`a`**, **`b`**: floats
  - **Divide** raises **`ValueError`** on division by zero

No resources, no prompts—**tools only**, and only this one tool.

---

## Part 7 — Run the server (stdio)

From the project root:

```powershell
uv run python server.py
```

This starts the MCP server on **stdio** (it may appear to “hang” with no output—that is normal; it is waiting for an MCP host).

Stop with **Ctrl+C**.

---

## Part 8 — Develop and inspect with MCP Inspector

Run (from the project root):

```powershell
uv run mcp dev server.py
```

Follow the CLI output to open **MCP Inspector** in the browser (commonly **`http://localhost:3000`**). There you can confirm the **`calculate`** tool schema and call it interactively.

When you are done, stop the dev server with **Ctrl+C**.

---

## Part 9 — Claude Desktop (Windows) configuration

Claude Desktop reads **`%AppData%\Claude\claude_desktop_config.json`**.

1. Open that file in an editor (create it if missing).
2. Merge a server entry like the following (adjust the **`--directory`** path to your **absolute** project folder).

```json
{
  "mcpServers": {
    "calculator": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\YourUser\\Documents\\GitHub\\YourProjectFolder",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

Notes:

- Use **escaped backslashes** (`\\`) in JSON on Windows.
- If `uv` is not found by Claude Desktop’s environment, set **`command`** to the **full path** returned by:

  ```powershell
  where.exe uv
  ```

3. **Fully quit and restart** Claude Desktop after saving the file.

---

## Part 10 — Troubleshooting

### `uv sync` tries to compile `pydantic-core` / Rust / MSVC errors

- Prefer **Python 3.12 or 3.13** (this repo blocks **3.14** in `pyproject.toml` for that reason).
- Install **“Build Tools for Visual Studio”** with **Desktop development with C++** only if you truly must compile native wheels locally.

### `uv` or `python` not found after install

- Close **all** terminals and reopen.
- Confirm `uv` with `where.exe uv` and Python with `py -0p`.

### Claude Desktop never shows tools

- Confirm **`claude_desktop_config.json`** JSON is valid.
- Confirm **`--directory`** points at the folder that contains **`pyproject.toml`** and **`server.py`**.
- Confirm **`uv run python server.py`** works manually from that folder.

---

## Quick command recap

```powershell
uv python install 3.12
uv python pin 3.12
uv sync
uv run python -c "import mcp; print(mcp.__version__)"
uv run mcp --help
uv run python server.py
uv run mcp dev server.py
```

---

## References

- MCP concepts and clients: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
- MCP Python SDK repository: [https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
