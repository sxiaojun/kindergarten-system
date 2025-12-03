from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KindergartenViewSet

# 创建路由器
router = DefaultRouter()

# 注册幼儿园视图集，注意这里不再添加'kindergartens'前缀
router.register(r'', KindergartenViewSet)

# 定义URL模式
urlpatterns = [
    # 包含路由器生成的URL
    path('', include(router.urls)),
]