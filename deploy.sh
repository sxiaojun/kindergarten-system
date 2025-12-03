#!/bin/bash

# 部署幼儿园管理系统脚本

set -e  # 遇到错误时停止执行

echo "开始部署幼儿园管理系统..."

# 检查 Docker 是否安装
if ! command -v docker >/dev/null 2>&1; then
    echo "错误: 未检测到 Docker，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "错误: 未检测到 Docker Compose，请先安装 Docker Compose"
    exit 1
fi

echo "Docker 版本: $(docker --version)"
echo "Docker Compose 版本: $(docker-compose --version)"

# 检查必要的文件是否存在（相对于当前目录）
echo "检查必需的配置文件..."
if [ ! -f "docker-compose.yml" ]; then
    echo "错误: docker-compose.yml 文件不存在"
    exit 1
fi

if [ ! -f "Dockerfile.backend" ]; then
    echo "错误: Dockerfile.backend 文件不存在"
    exit 1
fi

if [ ! -f "Dockerfile.frontend" ]; then
    echo "错误: Dockerfile.frontend 文件不存在"
    exit 1
fi

if [ ! -f "nginx.conf" ]; then
    echo "错误: nginx.conf 文件不存在"
    exit 1
fi

if [ ! -f "kindergarten_system/requirements.txt" ]; then
    echo "错误: kindergarten_system/requirements.txt 文件不存在"
    exit 1
fi

if [ ! -f "frontend/nginx-frontend.conf" ]; then
    echo "错误: frontend/nginx-frontend.conf 文件不存在"
    exit 1
fi

echo "所有必需文件检查通过!"

# 停止并删除当前项目的容器（如果有的话）
echo "停止并删除当前项目的容器..."
docker-compose down

# 构建并启动所有服务
echo "开始构建和启动 Docker 容器..."
docker-compose up --build -d

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 运行数据库迁移
echo "运行数据库迁移..."
docker-compose exec backend python manage.py migrate

# 收集静态文件
echo "收集静态文件..."
docker-compose exec backend python manage.py collectstatic --noinput

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

echo "部署完成!"
echo "您可以通过以下方式访问应用:"
echo "- 前端页面: http://your_server_ip"
echo "- 后端API: http://your_server_ip/api/"
echo "- 管理后台: http://your_server_ip/admin/"

echo "注意：如果您需要创建超级用户账户，请运行："
echo "docker-compose exec backend python manage.py createsuperuser"
