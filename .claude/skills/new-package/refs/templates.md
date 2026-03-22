# File Templates for new-package skill

Replace all `{feature}`, `{Feature}`, `{FEATURE}` placeholders with the actual feature name.
Replace `{description}` with a short description of the API.
Replace `{api_base}` with the API base URL.
Replace `{auth_env_var}` with the auth env var name (or remove if not needed).
Replace `{tags}` with relevant tags for the feature.

---

## `__init__.py`

```python
"""Feature {Feature} — {description}."""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="{feature}",
    description="{description}",
    version="0.1.0",
    api_base="{api_base}",
    requires_auth=False,  # Set True + auth_env_var if API needs a key
    tags=[{tags}],
)
```

If the API requires authentication:

```python
FEATURE_META = FeatureMeta(
    name="{feature}",
    description="{description}",
    version="0.1.0",
    api_base="{api_base}",
    requires_auth=True,
    auth_env_var="{auth_env_var}",
    tags=[{tags}],
)
```

---

## `constants.py`

```python
"""Constants for the {Feature} feature."""

# API base URL
{FEATURE}_API_BASE = "{api_base}"

# Add endpoint URLs, enums, category lists, etc.
# Example:
# ENDPOINT_FOO = f"{{{FEATURE}_API_BASE}}/foo"
# ENDPOINT_BAR = f"{{{FEATURE}_API_BASE}}/bar"
```

Rules:
- Zero imports from other project modules
- Only literals, dicts, lists, and string constants
- Use UPPER_SNAKE_CASE for all constants

---

## `schemas.py`

```python
"""Pydantic schemas for the {Feature} feature."""

from __future__ import annotations

from pydantic import BaseModel


# Define your Pydantic models here.
# Each model should represent a response or sub-object from the API.
#
# Example:
#
# class ExemploItem(BaseModel):
#     """Description of the item."""
#
#     id: int
#     nome: str
#     valor: float | None = None
```

Rules:
- Zero logic — only BaseModel definitions
- Use `from __future__ import annotations` for forward references
- Use `Field(description=...)` for non-obvious fields
- Use `| None = None` for optional fields

---

## `client.py`

```python
"""HTTP client for the {Feature} API.

Endpoints:
    - TODO: List API endpoints here
"""

from __future__ import annotations

from typing import Any

from mcp_brasil._shared.http_client import http_get

from .constants import {FEATURE}_API_BASE


# Implement async functions that call the API and return Pydantic models.
#
# Example:
#
# async def listar_items() -> list[Item]:
#     """Fetch all items from the API."""
#     data: list[dict[str, Any]] = await http_get(
#         f"{{{FEATURE}_API_BASE}}/items"
#     )
#     return [Item(**d) for d in data]
```

Rules:
- All functions are `async def`
- Use `http_get()` from `_shared.http_client` (handles retry/backoff)
- Return Pydantic models, NOT formatted strings
- Never format data for LLM consumption
- Document the API endpoint in the docstring

---

## `tools.py`

```python
"""Tool functions for the {Feature} feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
    - Uses Context for structured logging and progress reporting
"""

from __future__ import annotations

from fastmcp import Context

from mcp_brasil._shared.formatting import markdown_table, truncate_list

from . import client


# Implement tool functions that call client functions and format results.
# Always accept `ctx: Context` as a parameter for logging.
# FastMCP injects Context automatically — transparent to MCP clients.
#
# Example:
#
# async def listar_items(ctx: Context) -> str:
#     """Lista todos os items disponíveis.
#
#     Descrição detalhada para o LLM saber quando chamar esta tool.
#
#     Returns:
#         Tabela com os items.
#     """
#     await ctx.info("Buscando items...")
#     items = await client.listar_items()
#     rows = [(str(i.id), i.nome) for i in items]
#     return markdown_table(["ID", "Nome"], rows)
```

Rules:
- All functions are `async def`
- Each function has a complete docstring (used by LLM)
- Accept `ctx: Context` parameter for structured logging
- Use `await ctx.info(...)` for logging, `await ctx.report_progress(n, total)` for progress
- Delegate HTTP to client.py
- Return formatted strings using helpers from `_shared.formatting`:
  - `markdown_table(headers, rows)` — for tabular data
  - `truncate_list(items, max_items)` — for long lists
  - `format_brl(value)` — for BRL currency
  - `format_number_br(value, decimals)` — for BR locale numbers
  - `format_percent(value)` — for percentages

---

## `resources.py`

```python
"""Static reference data for the {Feature} feature.

Resources are read-only data sources that clients can pull.
They provide context to LLMs without requiring tool calls.

Resources are registered with data:// URIs (without the feature namespace —
mount() adds the namespace prefix automatically).
"""

from __future__ import annotations

import json


# Implement resource functions that return static reference data as JSON strings.
# These should NOT make HTTP calls — only return pre-computed/hardcoded data.
#
# Example:
#
# def catalogo_items() -> str:
#     """Catálogo completo de items disponíveis."""
#     items = [
#         {"id": 1, "nome": "Item A", "categoria": "Cat 1"},
#         {"id": 2, "nome": "Item B", "categoria": "Cat 2"},
#     ]
#     return json.dumps(items, ensure_ascii=False, indent=2)
```

Rules:
- Return JSON strings (not dicts) — use `json.dumps(data, ensure_ascii=False)`
- Functions are sync (not async) — they return static data
- No HTTP calls — only pre-computed data from constants.py or hardcoded
- Provide useful context for LLMs (reference tables, catalogs, key indicators)
- Good resource candidates: lists of categories, code tables, key indicators

---

## `prompts.py`

```python
"""Analysis prompts for the {Feature} feature.

Prompts are reusable templates that guide LLM interactions.
They instruct the LLM on which tools to call and how to analyze the data.

In Claude Desktop, prompts appear as selectable options (similar to slash commands).
"""

from __future__ import annotations


# Implement prompt functions that return instruction strings.
# These guide the LLM to use the feature's tools effectively.
#
# Example:
#
# def analise_item(nome: str) -> str:
#     \"\"\"Análise detalhada de um item.
#
#     Gera uma análise completa usando as tools da feature.
#
#     Args:
#         nome: Nome do item para analisar.
#     \"\"\"
#     return (
#         f"Analise o item '{nome}' seguindo estes passos:\\n\\n"
#         "1. Use a tool `listar_items` para ver todos os items\\n"
#         "2. Use a tool `buscar_detalhes` para obter detalhes\\n"
#         "3. Apresente um resumo com os dados encontrados"
#     )
```

Rules:
- Return `str` (auto-wrapped as user message by FastMCP)
- Functions are sync (not async) — they return templates
- Include clear instructions for the LLM on which tools to call
- Reference tools by their feature-local name (namespace is added automatically)
- Good prompt candidates: analysis workflows, data comparisons, summaries

---

## `server.py`

```python
"""{Feature} feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import (
    # Import your prompt functions here
)
from .resources import (
    # Import your resource functions here
)
from .tools import (
    # Import your tool functions here
)

mcp = FastMCP("mcp-brasil-{feature}")

# Tools
# mcp.tool(listar_items)
# mcp.tool(buscar_item)

# Resources (URIs without namespace prefix — mount adds "{feature}/" automatically)
# mcp.resource("data://catalogo", mime_type="application/json")(catalogo_items)
# mcp.resource("data://categorias", mime_type="application/json")(categorias_items)

# Prompts
# mcp.prompt(analise_item)
```

Rules:
- Zero business logic
- `mcp.tool(fn)`, `mcp.resource("uri")(fn)`, `mcp.prompt(fn)` calls only
- The `mcp` variable name is required (auto-registry expects it)
- FastMCP name should be `"mcp-brasil-{feature}"`
- Resource URIs MUST NOT include the feature name (mount adds namespace automatically)
- Use `mime_type="application/json"` for JSON resources

---

## Test structure

After creating the feature, also create the test directory:

```
tests/{feature}/
├── __init__.py
├── test_tools.py        # Mock client, test tool logic
├── test_client.py       # respx mock HTTP
├── test_resources.py    # Unit + Client integration tests for resources
├── test_prompts.py      # Unit + Client integration tests for prompts
└── test_integration.py  # fastmcp.Client e2e tests
```

Test patterns:
- `test_resources.py` — test JSON validity, data correctness, resource registration via `Client`
- `test_prompts.py` — test return values, parameter handling, prompt registration via `Client`
- `test_integration.py` — test tools, resources, and prompts via `fastmcp.Client(mcp)`
