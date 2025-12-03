#!/bin/bash

# 查看幼儿园管理系统日志脚本

# 进入项目目录
cd /home/root/kindergarten-system

if [ $# -eq 0 ]; then
    echo "使用方法: logs.sh [service_name]"
    echo "可用的服务:"
    echo "  - backend"
    echo "  - frontend"
    echo "  - db"
    echo "  - nginx"
    echo ""
    echo "也可以直接运行 'logs.sh' 查看所有服务的日志"
    exit 1
fi

if [ "$1" == "all" ]; then
    echo "显示所有服务的日志..."
    docker-compose logs -f
else
    echo "显示 $1 服务的日志..."
    docker-compose logs -f $1
fi
