from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChildViewSet

router = DefaultRouter()
router.register(r'', ChildViewSet, basename='child')

urlpatterns = [
    path('', include(router.urls)),
    # 其他自定义路径可以在这里添加
]