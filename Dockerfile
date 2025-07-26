# 数字员工系统生产级Docker镜像
# Digital Employee System Production Docker Image
#
# 构建目标：
# - 99.9%可用性
# - 1000并发支持
# - 自动扩容能力
# - 完整监控和日志

# =================== 第一阶段：基础环境 ===================
FROM python:3.11-slim-bullseye AS base

LABEL maintainer="Digital Employee Team"
LABEL version="2.0.0"
LABEL description="Enterprise Digital Employee Multi-Agent System"

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# 创建应用用户（安全最佳实践）
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    jq \
    libffi-dev \
    libssl-dev \
    pkg-config \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# =================== 第二阶段：依赖安装 ===================
FROM base AS dependencies

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt ./

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 升级pip和安装依赖
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install uvicorn[standard] gunicorn

# =================== 第三阶段：应用构建 ===================
FROM dependencies AS builder

# 复制源代码
COPY digital_employee_core/ ./digital_employee_core/
COPY docs/ ./docs/
COPY web_system/ ./web_system/
COPY memory_engine_module/ ./memory_engine_module/
COPY *.py ./
COPY *.md ./

# 设置Python路径
ENV PYTHONPATH="/app:$PYTHONPATH"

# 编译Python字节码（提升启动速度）
RUN python -m compileall digital_employee_core/ memory_engine_module/

# =================== 第四阶段：生产环境 ===================
FROM python:3.11-slim-bullseye AS production

# 复制基础环境配置
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:$PYTHONPATH" \
    PATH="/opt/venv/bin:$PATH" \
    \
    # 应用配置
    DIGITAL_EMPLOYEE_ENV=production \
    DIGITAL_EMPLOYEE_LOG_LEVEL=INFO \
    DIGITAL_EMPLOYEE_WORKERS=4 \
    DIGITAL_EMPLOYEE_MAX_REQUESTS=1000 \
    DIGITAL_EMPLOYEE_TIMEOUT=60 \
    \
    # 监控配置
    PROMETHEUS_PORT=8001 \
    HEALTH_CHECK_PORT=8002

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建应用用户和目录
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    mkdir -p /app /var/log/digital_employee /var/lib/digital_employee && \
    chown -R appuser:appuser /app /var/log/digital_employee /var/lib/digital_employee

# 复制虚拟环境
COPY --from=dependencies /opt/venv /opt/venv

# 复制应用代码
COPY --from=builder --chown=appuser:appuser /app /app

# 设置工作目录
WORKDIR /app

# 创建启动脚本
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# 健康检查\n\
echo "Starting Digital Employee System..."\n\
\n\
# 等待依赖服务\n\
if [ -n "$DATABASE_URL" ]; then\n\
    echo "Waiting for database..."\n\
    until pg_isready -d "$DATABASE_URL"; do\n\
        sleep 1\n\
    done\n\
fi\n\
\n\
if [ -n "$REDIS_URL" ]; then\n\
    echo "Waiting for Redis..."\n\
    until redis-cli -u "$REDIS_URL" ping; do\n\
        sleep 1\n\
    done\n\
fi\n\
\n\
# 启动应用\n\
exec gunicorn digital_employee_core.main:app \\\n\
    --bind 0.0.0.0:8000 \\\n\
    --workers $DIGITAL_EMPLOYEE_WORKERS \\\n\
    --worker-class uvicorn.workers.UvicornWorker \\\n\
    --max-requests $DIGITAL_EMPLOYEE_MAX_REQUESTS \\\n\
    --timeout $DIGITAL_EMPLOYEE_TIMEOUT \\\n\
    --keep-alive 5 \\\n\
    --log-level $DIGITAL_EMPLOYEE_LOG_LEVEL \\\n\
    --access-logfile /var/log/digital_employee/access.log \\\n\
    --error-logfile /var/log/digital_employee/error.log \\\n\
    --preload\n\
' > /app/start.sh && chmod +x /app/start.sh

# 创建健康检查脚本
RUN echo '#!/usr/bin/env python3\n\
import sys\n\
import requests\n\
import json\n\
from datetime import datetime\n\
\n\
def health_check():\n\
    """生产级健康检查"""\n\
    try:\n\
        # 检查主服务\n\
        response = requests.get("http://localhost:8000/health", timeout=5)\n\
        \n\
        if response.status_code != 200:\n\
            print(f"Health check failed: HTTP {response.status_code}")\n\
            return False\n\
        \n\
        health_data = response.json()\n\
        \n\
        # 检查关键组件\n\
        required_components = ["database", "redis", "agents", "entropy_engine"]\n\
        for component in required_components:\n\
            if health_data.get(component, {}).get("status") != "healthy":\n\
                print(f"Component {component} is unhealthy")\n\
                return False\n\
        \n\
        # 检查内存和CPU使用率\n\
        memory_usage = health_data.get("system", {}).get("memory_usage", 100)\n\
        if memory_usage > 90:\n\
            print(f"High memory usage: {memory_usage}%")\n\
            return False\n\
        \n\
        print(f"Health check passed at {datetime.now()}")\n\
        return True\n\
        \n\
    except Exception as e:\n\
        print(f"Health check error: {str(e)}")\n\
        return False\n\
\n\
if __name__ == "__main__":\n\
    if health_check():\n\
        sys.exit(0)\n\
    else:\n\
        sys.exit(1)\n\
' > /app/healthcheck.py && chmod +x /app/healthcheck.py

# 切换到应用用户
USER appuser

# 暴露端口
EXPOSE 8000 8001 8002

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python /app/healthcheck.py || exit 1

# 设置卷挂载点
VOLUME ["/var/log/digital_employee", "/var/lib/digital_employee"]

# 启动命令
CMD ["/app/start.sh"]

# =================== 开发阶段（可选） ===================
FROM builder AS development

# 安装开发依赖
RUN pip install pytest pytest-cov pytest-asyncio black flake8 mypy jupyter

USER appuser

# 开发环境启动命令
CMD ["uvicorn", "digital_employee_core.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]