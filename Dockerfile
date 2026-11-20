FROM python:3.13-slim-trixie

LABEL org.opencontainers.image.authors="Ma'ayan Lab <avi.maayan@mssm.edu>"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Upgrade packaging tools first so patched releases are used, then install the
# application dependencies in one layer.
COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --upgrade --requirement requirements.txt

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/similarity \
    && chown -R appuser:appuser /app

COPY --chown=appuser:appuser . .
RUN chmod 0755 /app/entrypoint.sh

USER appuser

EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
