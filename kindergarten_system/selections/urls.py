from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器实例
router = DefaultRouter()

# 注册选区定义视图集
router.register(r'selection-areas', views.SelectionAreaViewSet, basename='selection-area')

# 注册选区记录视图集
router.register(r'selection-records', views.SelectionRecordViewSet, basename='selection-record')

# 定义URL模式
urlpatterns = [
    # 包含路由器生成的所有URL
    path('', include(router.urls)),
    
    # 添加自定义URL（与视图集路由区分开）
    path('recent-activities/', views.get_recent_activities, name='recent-activities'),
    path('dashboard-stats/', views.get_dashboard_stats, name='dashboard-stats'),
]