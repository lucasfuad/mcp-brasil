FROM python:3.13-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first (cache-friendly layer)
COPY pyproject.toml uv.lock README.md ./

# Install production dependencies only
RUN uv sync --no-dev --frozen --no-install-project

# Copy source code
COPY src/ src/

# Install the project itself
RUN uv sync --no-dev --frozen

EXPOSE 8061

CMD ["uv", "run", "python", "-c", "from mcp_brasil.server import mcp; mcp.run(transport='streamable-http', host='0.0.0.0', port=8061)"]
