# 采集示例的运行镜像：只依赖 Python 与 Python 库，不需要数据库等外部中间件
FROM python:3.12-slim

# 关闭字节码、实时输出日志、pip 不缓存，默认离线运行避免误抓真实站点
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SPIDER_OFFLINE=1

WORKDIR /app

# 先装依赖，利用镜像层缓存
COPY requirements.txt .
# 支持通过 --build-arg PIP_INDEX_URL=... 使用内网或国内 PyPI 镜像
ARG PIP_INDEX_URL
RUN pip install --no-cache-dir -r requirements.txt ${PIP_INDEX_URL:+-i $PIP_INDEX_URL}

# 复制项目源码
COPY . .

# 创建数据目录，并以非 root 用户运行
RUN mkdir -p /app/data \
    && useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

# 默认执行离线演示；实际子命令由 docker-compose command 覆盖
ENTRYPOINT ["python", "main.py"]
