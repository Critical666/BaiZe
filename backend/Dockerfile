FROM python:3.12-slim

# 系统依赖（sentence-transformers 编译需要）
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 复制源代码
COPY . .

EXPOSE 8000

# 默认启动 API 服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
