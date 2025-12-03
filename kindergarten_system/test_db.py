print("测试开始")
import os
import sys
print("导入基础模块成功")

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("添加路径成功")

# 设置DJANGO_SETTINGS_MODULE环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kindergarten_system.settings')
print("设置环境变量成功")

try:
    # 导入Django并初始化
    import django
    print("导入Django成功")
    django.setup()
    print("Django初始化成功!")
    
    # 测试数据库连接
    from django.db import connection
    print("导入数据库连接成功")
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("数据库连接成功!")
        
    # 尝试获取所有已安装的应用
    from django.apps import apps
    print(f"已安装的应用: {[app.name for app in apps.get_app_configs()]}")
    
except Exception as e:
    print(f"发生错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("测试结束")
