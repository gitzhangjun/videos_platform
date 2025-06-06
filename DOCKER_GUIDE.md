# Docker 启动指南

## 快速启动

使用 Docker Compose 启动整个项目：

```bash
# 构建并启动所有服务
docker-compose up --build

# 在后台运行
docker-compose up --build -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 访问地址

- **前端应用**: http://localhost:8888
- **后端API**: http://localhost:5001

## 登录信息

### 硬编码管理员账户
- **用户名**: `admin`
- **密码**: `admin123456`

**注意**: 这是唯一的账户，直接硬编码在后端代码中，无需数据库。

## 重要说明

### 功能特性
- ✅ 简化登录认证（无数据库）
- ✅ 硬编码单一管理员账户
- ✅ Session会话管理
- ✅ 路由守卫保护
- ✅ 视频上传和播放
- ✅ 视频列表展示
- ✅ 视频预览功能
- ✅ 登出功能

### 架构简化
- ❌ 无数据库依赖
- ❌ 无用户注册功能
- ❌ 无复杂的用户管理
- ✅ 极简的认证方案

### 路径映射配置
项目已配置将本地视频文件夹映射到Docker容器中：
- **本地路径**: `D:/nginx-1.24.0/nginx-1.24.0/html/static/a/123`
- **容器路径**: `/app/videos`

**注意**: 如果您使用的是macOS或Linux系统，请修改 `docker-compose.yml` 中的路径为您的实际路径，例如：
```yaml
volumes:
  - "/Users/your-username/path/to/videos:/app/videos"
```

### 安全性说明
- 所有功能都需要登录后才能访问
- 会话管理通过Flask Session实现
- 路由守卫确保未登录用户自动跳转到登录页
- 简化架构，减少安全风险点

## 故障排除

### 1. 构建失败

如果构建过程中出现错误，请尝试：

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
docker-compose up
```

### 2. 端口冲突

如果端口被占用，请检查并关闭占用端口的程序：

```bash
# 查看端口占用情况
lsof -i :8888
lsof -i :5001

# 或者修改 docker-compose.yml 中的端口映射
```

### 3. 登录问题

如果无法登录：

1. 确认使用正确的账户信息：`admin` / `admin123456`
2. 检查后端日志：
   ```bash
   docker-compose logs backend
   ```
3. 清除浏览器缓存和Cookie
4. 检查网络连接

### 4. 前端无法访问后端

如果前端页面显示但API调用失败：

1. 检查后端服务是否正常启动：
   ```bash
   docker-compose logs backend
   ```

2. 检查网络连接：
   ```bash
   docker-compose exec frontend ping backend
   ```

### 5. 文件上传失败

如果视频上传失败：

1. 确认已登录
2. 检查文件大小限制（当前设置为1000M）
3. 检查文件格式是否支持
4. 查看后端日志：
   ```bash
   docker-compose logs backend
   ```

### 6. 视频文件映射问题

如果看不到本地视频文件：

1. 检查本地路径是否正确
2. 确保Docker有权限访问该路径
3. 检查路径格式（Windows使用 `D:/path`，macOS/Linux使用 `/path`）

### 7. Session问题

如果出现会话相关错误：

```bash
# 重启backend服务即可清除所有session
docker-compose restart backend
```

### 8. 前端构建失败

如果前端构建过程出现 Node.js 相关错误：

```bash
# 清理前端构建
docker-compose down
docker rmi video_platform_frontend
docker-compose build frontend --no-cache
```

## 开发模式

如果需要开发模式（代码热重载），可以：

1. 使用本地开发环境（参考 README.md）
2. 或者修改 docker-compose.yml 添加 volumes 映射

## 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs frontend
docker-compose logs backend

# 实时查看日志
docker-compose logs -f backend
```

## 清理环境

```bash
# 停止并删除容器
docker-compose down

# 删除相关镜像
docker rmi video_platform_frontend video_platform_backend

# 清理所有未使用的资源
docker system prune -a
```

## 常见问题

### Q: 为什么访问 localhost:8888 显示连接被拒绝？
A: 请确保 Docker 服务正在运行，并且端口没有被其他程序占用。

### Q: 如何修改管理员密码？
A: 在 `backend/app.py` 中修改 `ADMIN_PASSWORD` 变量，然后重新构建容器。

### Q: 上传的视频在哪里存储？
A: 视频文件存储在映射的本地目录中，同时也在后端容器的 `/app/videos` 目录中。

### Q: 如何修改视频存储路径？
A: 编辑 `docker-compose.yml` 文件中的 volumes 映射，将左侧路径改为您的目标路径。

### Q: 可以修改端口吗？
A: 可以，编辑 `docker-compose.yml` 文件中的端口映射，例如将 `8888:8888` 改为 `3000:8888`。

### Q: 为什么不使用数据库？
A: 为了简化部署和维护，只需要一个管理员账户，硬编码即可满足需求，避免数据库相关问题。

### Q: 可以添加更多用户吗？
A: 当前设计为单用户系统，如需多用户支持，需要重新引入数据库或其他存储方案。 