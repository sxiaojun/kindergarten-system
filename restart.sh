#!/bin/bash

# 重启幼儿园管理系统脚本

echo "重启幼儿园管理系统..."

# 进入项目目录
cd /home/root/kindergarten-system

# 停止当前项目的所有服务
echo "停止当前项目的所有服务..."
docker-compose stop

# 启动当前项目的所有服务
echo "启动当前项目的所有服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

echo "服务重启完成!"
