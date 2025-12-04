#!/bin/bash
# 备份数据库
docker-compose exec db mysqldump -u kindergarten_user -pkindergarten_password kindergarten_db > kindergarten_db_backup.sql

# 备份媒体文件
docker run --rm -v kindergartenSystem_media_data:/source -v $(pwd):/backup alpine tar czf /backup/media_backup.tar.gz -C /source .

# 打包项目代码（如果需要）
tar czf kindergarten_system.tar.gz --exclude=node_modules --exclude=.git .

echo "备份完成，请将以下文件复制到新服务器："
echo "1. kindergarten_db_backup.sql"
echo "2. media_backup.tar.gz"
echo "3. kindergarten_system.tar.gz"
