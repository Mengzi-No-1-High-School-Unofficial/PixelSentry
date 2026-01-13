FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libasound2 \
    libdbus-glib-1-2 \
    libx11-xcb1 \
    libxt6 \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv 到系统路径
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx

# 复制项目文件
COPY pyproject.toml ./
COPY app ./app

# 安装 Python 依赖
RUN uv pip install --system -e .

# 安装 Playwright 浏览器
RUN playwright install chromium
RUN playwright install-deps chromium

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
