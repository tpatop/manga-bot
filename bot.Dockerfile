FROM python:3.11.6-slim-bullseye

ENV \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN apt-get update && \
  apt-get install --no-install-recommends -y \
  build-essential \
  gettext \
  libpq-dev \
  wget && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "sh", "-c", "alembic upgrade head; python main.py"]
