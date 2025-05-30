FROM node:20-slim AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install --production=false --force

COPY . .

# 使用 Node.js 直接执行 Vite
RUN node node_modules/vite/bin/vite.js build