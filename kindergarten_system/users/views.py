import base64
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.cache import cache
from django.contrib.auth import authenticate
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserRegisterSerializer
)
from .permissions import (
    IsSystemOwner,
    IsKindergartenOwnerOrSystemOwner,
    IsAuthenticatedAndHasRole,
    KindergartenDataPermission,
    IsOwnerOrReadOnly
)

# 自定义令牌获取视图
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# 生成验证码
def generate_captcha():
    # 生成随机字符串
    def gen_text():
        return ''.join(random.sample(string.ascii_letters + string.digits, 4))
    
    # 创建图像
    def draw_captcha(text):
        width, height = 120, 40
        # 创建图像
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        # 创建字体对象
        try:
            font = ImageFont.truetype('arial.ttf', 24)
        except:
            font = ImageFont.load_default()
        # 创建绘图对象
        draw = ImageDraw.Draw(image)
        
        # 绘制文本（适配新版本Pillow）
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # fallback方案
            text_width, text_height = 40, 20
            
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, font=font, fill=(0, 0, 0))
        
        # 绘制干扰线
        for _ in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        return image
    
    # 生成验证码文本和图像
    captcha_text = gen_text()
    captcha_image = draw_captcha(captcha_text)
    
    # 将图像转换为base64编码
    buffered = BytesIO()
    captcha_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # 生成唯一key
    key = ''.join(random.sample(string.ascii_letters + string.digits, 32))
    
    # 将验证码文本存储到缓存中，有效期5分钟
    cache.set(f'captcha_{key}', captcha_text.lower(), 300)
    
    return key, img_str

# 用户视图集
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'phone']
    ordering_fields = ['id', 'username', 'created_at']
    parser_classes = (JSONParser,)
    
    def get_permissions(self):
        """
        根据不同操作设置不同的权限
        """
        if self.action == 'create':
            # 用户注册允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'list':
            # 用户列表根据角色筛选
            return [IsAuthenticatedAndHasRole()]
        elif self.action == 'retrieve':
            # 获取用户信息可以是系统所有者、园长或本人
            return [IsKindergartenOwnerOrSystemOwner() or IsOwnerOrReadOnly()]
        elif self.action == 'update' or self.action == 'partial_update':
            # 更新用户信息可以是系统所有者、园长或本人
            return [IsKindergartenOwnerOrSystemOwner() or IsOwnerOrReadOnly()]
        elif self.action == 'destroy':
            # 删除用户仅允许系统所有者
            return [IsSystemOwner()]
        elif self.action == 'me':
            # 获取当前用户信息
            return [IsAuthenticated()]
        elif self.action == 'captcha' or self.action == 'login' or self.action == 'change_password':
            # 获取验证码、登录和修改密码不需要认证
            return [AllowAny()]
        elif self.action == 'change_current_password':
            # 修改当前用户密码需要认证
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        根据用户角色过滤查询集
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # 如果是系统所有者，返回所有用户
        if hasattr(user, 'role') and user.role == 'owner':
            return queryset
        
        # 如果是园长，返回自己幼儿园的所有用户
        elif hasattr(user, 'role') and user.role == 'principal' and user.kindergarten:
            return queryset.filter(kindergarten=user.kindergarten)
        
        # 如果是教师，返回自己
        elif hasattr(user, 'role') and user.role == 'teacher':
            return queryset.filter(id=user.id)
        
        return queryset.none()
    
    def create(self, request, *args, **kwargs):
        """
        创建用户
        """
        # 对于系统所有者创建用户，使用UserSerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        获取当前用户信息
        """
        serializer = self.get_serializer(request.user)
        return Response({
            'code': 200,
            'msg': '获取用户信息成功',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsSystemOwner])
    def activate(self, request, pk=None):
        """
        激活用户
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'user activated'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsSystemOwner])
    def deactivate(self, request, pk=None):
        """
        停用用户
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def teachers(self, request):
        """
        获取教师列表
        """
        queryset = self.get_queryset().filter(role='teacher')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def kindergartens(self, request):
        """
        获取园长列表
        """
        queryset = self.get_queryset().filter(role='principal')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def captcha(self, request):
        """
        获取验证码
        """
        key, img_str = generate_captcha()
        return Response({
            'code': 200,
            'msg': '获取验证码成功',
            'data': {
                'key': key,
                'image': f'data:image/png;base64,{img_str}'
            }
        })
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        用户登录
        """
        username = request.data.get('username')
        password = request.data.get('password')
        captcha = request.data.get('captcha')
        captcha_key = request.data.get('captchaKey')
        
        # 验证验证码
        if not captcha_key or not captcha:
            return Response({'code': 400, 'msg': '验证码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 从缓存中获取验证码
        cached_captcha = cache.get(f'captcha_{captcha_key}')
        if not cached_captcha:
            return Response({'code': 400, 'msg': '验证码已过期'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证验证码是否正确
        if cached_captcha != captcha.lower():
            return Response({'code': 400, 'msg': '验证码错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证用户名和密码
        if not username or not password:
            return Response({'code': 400, 'msg': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'code': 400, 'msg': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_active:
            return Response({'code': 400, 'msg': '用户已被禁用'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        
        # 删除已使用的验证码
        cache.delete(f'captcha_{captcha_key}')
        
        return Response({
            'code': 200,
            'msg': '登录成功',
            'data': {
                'token': str(refresh.access_token),
                'user': UserSerializer(user).data
            }
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        用户登出
        """
        # 在实际应用中，你可能想要将token加入黑名单
        # 但由于JWT的无状态特性，这里只是简单地返回成功
        return Response({
            'code': 200,
            'msg': '登出成功'
        })

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def change_password(self, request):
        """
        修改密码（无需旧密码验证）
        """
        username = request.data.get('username')
        new_password = request.data.get('new_password')
        captcha = request.data.get('captcha')
        captcha_key = request.data.get('captcha_key')
        
        # 验证验证码
        if not captcha_key or not captcha:
            return Response({'code': 400, 'msg': '验证码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 从缓存中获取验证码
        cached_captcha = cache.get(f'captcha_{captcha_key}')
        if not cached_captcha:
            return Response({'code': 400, 'msg': '验证码已过期'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证验证码是否正确
        if cached_captcha != captcha.lower():
            return Response({'code': 400, 'msg': '验证码错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证用户名和新密码
        if not username or not new_password:
            return Response({'code': 400, 'msg': '用户名和新密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 查找用户
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'code': 400, 'msg': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        # 删除已使用的验证码
        cache.delete(f'captcha_{captcha_key}')
        
        return Response({
            'code': 200,
            'msg': '密码修改成功'
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_current_password(self, request):
        """
        修改当前用户密码（无需旧密码验证）
        """
        new_password = request.data.get('new_password')
        
        # 验证新密码
        if not new_password:
            return Response({'code': 400, 'msg': '新密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取当前用户
        user = request.user
        
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        return Response({
            'code': 200,
            'msg': '密码修改成功，请重新登录'
        })

# 用户注册视图
class UserRegisterViewSet(viewsets.GenericViewSet):
    serializer_class = UserRegisterSerializer
    permission_classes = [IsSystemOwner]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        用户注册
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 返回创建的用户信息（不包含密码）
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)