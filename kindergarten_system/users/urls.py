from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    CustomTokenObtainPairView,
    UserViewSet,
    UserRegisterViewSet
)

# 创建路由器
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'register', UserRegisterViewSet, basename='register')

# 用户认证相关路由
urlpatterns = [
    # JWT认证路由
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # 登录接口
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    
    # 登出接口
    path('logout/', UserViewSet.as_view({'post': 'logout'}), name='logout'),
    
    # 修改密码接口
    path('change_password/', UserViewSet.as_view({'post': 'change_password'}), name='change_password'),
    
    # 修改当前用户密码接口
    path('users/change_password/', UserViewSet.as_view({'post': 'change_current_password'}), name='change_current_password'),
    
    # 验证码接口
    path('inter_captcha/', UserViewSet.as_view({'get': 'captcha'}), name='captcha'),
    
    # 包含路由器的路由
    path('', include(router.urls)),
]