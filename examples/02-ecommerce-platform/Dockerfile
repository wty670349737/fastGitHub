FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
# 支持通过 --build-arg PIP_INDEX_URL=... 使用内网或国内 PyPI 镜像
ARG PIP_INDEX_URL
RUN pip install --no-cache-dir -r requirements.txt ${PIP_INDEX_URL:+-i $PIP_INDEX_URL}

COPY app ./app
RUN mkdir -p /app/data \
    && useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
