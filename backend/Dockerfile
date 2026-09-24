FROM python:3.12.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements-runtime.lock ./
RUN python -m pip install --no-cache-dir -r requirements-runtime.lock \
    && groupadd --gid 10001 toojunto \
    && useradd --uid 10001 --gid toojunto --no-create-home --shell /usr/sbin/nologin toojunto

COPY --chown=toojunto:toojunto app ./app

USER toojunto

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
