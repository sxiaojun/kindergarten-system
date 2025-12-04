# 1. 解压项目代码（如果打包了）
tar xzf kindergarten_system.tar.gz

# 2. 进入项目目录
cd kindergartenSystem

# 3. 构建镜像
docker-compose build

# 4. 启动服务（只启动，不导入数据）
docker-compose up -d

# 5. 等待服务启动完成
sleep 30

# 6. 导入数据库数据
docker cp kindergarten_db_backup.sql kindergartenSystem-db-1:/tmp/
docker-compose exec db mysql -u kindergarten_user -pkindergarten_password kindergarten_db -e "source /tmp/kindergarten_db_backup.sql"

# 7. 恢复媒体文件
docker run --rm -v kindergartenSystem_media_data:/target -v $(pwd):/backup alpine sh -c "tar xzf /backup/media_backup.tar.gz -C /target"

# 8. 重启服务以确保一切正常
docker-compose restart


# 检查服务状态
docker-compose ps

# 检查数据库数据
docker-compose exec backend python manage.py shell

# 检查媒体文件
docker-compose exec backend ls -la /app/media/child_avatars/
