FROM python:3.13-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir uv && \
    uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv pip install --system fastapi uvicorn itsdangerous openai sqlalchemy bcrypt python-dotenv pydantic

# Copy application code
COPY app ./app

# Create data directory for SQLite
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run the application with venv activated
ENV PATH="/app/.venv/bin:$PATH"
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000
