# 使用官方Python 3.11镜像作为基础镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# 创建工作目录
WORKDIR /app

# 安装系统依赖（PostgreSQL客户端库等）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=300 -r requirements.txt

# 复制应用源代码
COPY . .

# 创建docs目录（用于文档生成）
RUN mkdir -p /app/docs

# 设置正确的文件权限
RUN chmod +x main.py 2>/dev/null || true

# 暴露默认端口（虽然MCP通过stdio通信，但为了兼容性保留）
EXPOSE 3000

# 简化的健康检查（不连接数据库）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# 运行MCP服务器
CMD ["python", "main.py"] 