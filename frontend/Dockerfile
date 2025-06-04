# 使用官方 Node.js 运行时作为父镜像
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 将 package.json 和 package-lock.json 复制到工作目录
COPY package*.json ./

# 安装依赖
RUN npm ci

# 将项目文件复制到工作目录
COPY . .

# 构建前端应用
RUN npx vite build

# 使用 Nginx 提供静态文件
FROM nginx:stable-alpine

# 复制构建的文件
COPY --from=0 /app/dist /usr/share/nginx/html

# 复制自定义Nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 8888

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]