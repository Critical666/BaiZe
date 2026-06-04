# 阶段1：构建前端静态资源
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --registry=https://registry.npmmirror.com

COPY . .
RUN npm run build

# 阶段2：Nginx 服务静态资源
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
