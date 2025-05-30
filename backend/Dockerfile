# 使用官方 Python 运行时作为父镜像
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器中的 /app
COPY . /app

# 安装任何所需的包
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 5001

# 定义环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 运行 app.py
CMD ["flask", "run", "--port", "5001"]