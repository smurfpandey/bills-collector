FROM python:3.12-slim-bullseye AS python-base

# Setup env
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV POETRY_VERSION=1.8.2
# make poetry install to this location
ENV POETRY_HOME="/opt/poetry"
# make poetry create the virtual environment in the project's root
# it gets named `.venv`
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
# do not ask any interactive question
ENV POETRY_NO_INTERACTION=1

ENV PYSETUP_PATH="/opt/pysetup"
ENV VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install runtime dependencies
RUN apt update && apt install -y libpq5

FROM python-base AS builder-base

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
# The --mount will mount the buildx cache directory to where
# Poetry and Pip store their cache so that they can re-use it
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python3 -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN --mount=type=cache,target=/root/.cache \
    poetry install

FROM node:20.11.1-alpine3.19 AS node-base

COPY . /app/
WORKDIR /app

RUN npm ci
RUN npm run build

################################
# PRODUCTION
# Final image used for runtime
################################
FROM python-base AS production

ENV FASTAPI_ENV=production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY . /app/
COPY --from=node-base /app/bills_collector/static/dist /app/bills_collector/static/dist
RUN chmod +x /app/entrypoint.sh
WORKDIR /app

CMD [ "/app/entrypoint.sh" ]
