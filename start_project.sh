#!/bin/bash

# 定义项目根目录
PROJECT_ROOT="$(dirname "$(readlink -f "$0")")"

# 1. 删除后端数据库文件
DB_PATH="$PROJECT_ROOT/backend/instance/users.db"
if [ -f "$DB_PATH" ]; then
    echo "Deleting $DB_PATH..."
    rm "$DB_PATH"
    echo "$DB_PATH deleted."
else
    echo "$DB_PATH not found, skipping deletion."
fi

# 2. 启动后端服务
echo "Starting backend service..."
cd "$PROJECT_ROOT/backend"
# 检查是否安装了venv，如果没有则创建并激活
if [ ! -d "venv" ]; then
    echo "Creating virtual environment for backend..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

source venv/bin/activate

# 检查并安装后端依赖
if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt not found in backend directory. Please ensure it exists."
    exit 1
fi

pip install -r requirements.txt

# 以后台方式运行Flask应用
FLASK_APP=app.py FLASK_DEBUG=1 flask run --host=0.0.0.0 --port=5001 &
BACKEND_PID=$!
echo "Backend service started with PID: $BACKEND_PID"
cd "$PROJECT_ROOT"

# 3. 启动前端服务
echo "Starting frontend service..."
cd "$PROJECT_ROOT/frontend"
# 检查并安装前端依赖
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
    echo "Frontend dependencies installed."
fi
npm run dev &
FRONTEND_PID=$!
echo "Frontend service started with PID: $FRONTEND_PID"
cd "$PROJECT_ROOT"

echo "Project services started. Press Ctrl+C to stop them."

# 等待所有后台进程结束
wait $BACKEND_PID $FRONTEND_PID