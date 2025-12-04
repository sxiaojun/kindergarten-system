#!/bin/bash
echo "解压项目文件..."
tar xzf kindergarten_system.tar.gz

echo "启动服务..."
cd kindergartenSystem
docker-compose up -d

echo "等待服务启动..."
sleep 30

echo "恢复数据库..."
docker cp kindergarten_db_backup.sql kindergartenSystem-db-1:/tmp/
docker-compose exec db mysql -u kindergarten_user -pkindergarten_password kindergarten_db -e "source /tmp/kindergarten_db_backup.sql"

echo "恢复媒体文件..."
docker run --rm -v kindergartenSystem_media_data:/target -v $(pwd):/backup alpine sh -c "tar xzf /backup/media_backup.tar.gz -C /target"

echo "重启服务以确保一切正常..."
docker-compose restart

echo "迁移完成！"
