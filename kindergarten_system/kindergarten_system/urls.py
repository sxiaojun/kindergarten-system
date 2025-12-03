"""
URL configuration for kindergarten_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

# API路由配置
api_urlpatterns = [
    # 用户认证相关路由
    path('auth/', include('users.urls')),
    # 幼儿园应用路由
    path('kindergartens/', include('kindergartens.urls')),
    # 班级应用路由
    path('classes/', include('classes.urls')),
    # 教师应用路由
    path('teachers/', include('teachers.urls')),
    # 选区应用路由
    path('selections/', include('selections.urls')),
    path('children/', include('children.urls')),
    # 其他应用的路由将在这里添加

]

def root_view(request):
    return JsonResponse({
        'message': '幼儿园管理系统API服务',
        'version': '1.0',
        'available_endpoints': {
            'admin': '/admin/',
            'auth': '/auth/',
            'kindergartens': '/kindergartens/',
            'classes': '/classes/',
            'teachers': '/teachers/',
            'selections': '/selections/',
            'children': '/children/'
        }
    }, json_dumps_params={'ensure_ascii': False})

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    # API路由
    path('api/', include(api_urlpatterns)),
]

# 开发环境下的媒体文件路由
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)