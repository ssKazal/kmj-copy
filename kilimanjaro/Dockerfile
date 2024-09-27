FROM python:3.9.6

ARG kilimanjaro

ENV kilimanjaro=${kilimanjaro} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.8


# System deps:
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /kilimanjaro
COPY pyproject.toml /kilimanjaro/
# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$kilimanjaro" == production && echo "--no-dev") --no-interaction --no-ansi

COPY . /kilimanjaro