#!/bin/bash

# 初始化数据库脚本

echo "开始初始化数据库..."

# 运行 Django 数据库迁移
echo "运行数据库迁移..."
docker-compose exec backend python manage.py migrate

# 收集静态文件
echo "收集静态文件..."
docker-compose exec backend python manage.py collectstatic --noinput

echo "数据库初始化完成!"
echo "提示：如果您需要创建超级用户，请运行："
echo "docker-compose exec backend python manage.py createsuperuser"
