#!/bin/bash

# 更新幼儿园管理系统脚本

set -e  # 遇到错误时停止执行

echo "开始更新幼儿园管理系统..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null
then
    echo "错误: 未检测到 Docker，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null
then
    echo "错误: 未检测到 Docker Compose，请先安装 Docker Compose"
    exit 1
fi

# 进入项目目录
cd /home/root/kindergarten-system

# 拉取最新的代码
echo "拉取最新的代码..."
git pull origin master

# 检查是否有更新
if git diff-index --quiet HEAD --; then
    echo "没有检测到代码更新"
else
    echo "检测到代码更新，开始重新构建..."

    # 停止当前项目的容器
    echo "停止当前项目的容器..."
    docker-compose stop

    # 重新构建服务
    echo "重新构建服务..."
    docker-compose build

    # 启动服务
    echo "启动服务..."
    docker-compose up -d

    # 等待服务启动
    echo "等待服务启动..."
    sleep 30

    # 检查是否需要运行数据库迁移
    echo "检查是否需要运行数据库迁移..."
    docker-compose exec backend python manage.py makemigrations --check --dry-run
    if [ $? -ne 0 ]; then
        echo "检测到数据库模型变更，运行迁移..."
        docker-compose exec backend python manage.py migrate
    else
        echo "数据库模型无变更，跳过迁移"
    fi

    # 重新收集静态文件
    echo "重新收集静态文件..."
    docker-compose exec backend python manage.py collectstatic --noinput --clear
    docker-compose exec backend python manage.py collectstatic --noinput

    # 检查服务状态
    echo "检查服务状态..."
    docker-compose ps

    echo "更新完成!"
fi
