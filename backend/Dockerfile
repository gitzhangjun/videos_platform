# 使用官方 Python 运行时作为父镜像
FROM python:3.9-slim


# 确保 sources.list 存在并替换镜像源
RUN echo "检查 sources.list 文件..." && \
    if [ ! -f /etc/apt/sources.list ]; then \
        echo "sources.list 不存在，创建新文件" && \
        echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
        echo "deb http://deb.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list; \
    fi && \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    apt-get update -y


# 设置工作目录
WORKDIR /app

# 安装系统依赖（添加重试机制）
RUN apt-get update --allow-releaseinfo-change && \
    apt-get install -y --no-install-recommends --fix-missing \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p videos videos/imgs

# 暴露端口
EXPOSE 5001

# 启动命令
CMD ["python", "app.py"]