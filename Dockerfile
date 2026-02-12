FROM python:3.14-slim

WORKDIR /app

# System deps for psycopg2 and matplotlib
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY App/ ./App/
COPY main.py ./

# Create exports directory for generated files
RUN mkdir -p exports

EXPOSE 8000

# Run migrations then start the API server
CMD uv run alembic upgrade head && uv run python main.py
