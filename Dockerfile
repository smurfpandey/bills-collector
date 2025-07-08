# Install uv
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# Copy the project into the intermediate image
COPY . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

##########################################
# Build frontend
##########################################
FROM node:22-slim AS frontend-build

# Change the working directory to the `app` directory
WORKDIR /app

COPY package*.json /app/
RUN npm ci

COPY . /app
RUN npm run build

##########################################
# Prepare the final image
##########################################
FROM python:3.12-slim

WORKDIR /app

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Install application into container
COPY . /app
COPY --from=frontend-build /app/bills_collector/static /app/bills_collector/static

# Run the application
ENV PATH="/app/.venv/bin:$PATH"
CMD ["gunicorn", "-w 4", "-b 0.0.0.0:5000", "--preload", "bills_collector.app:create_app()"]

