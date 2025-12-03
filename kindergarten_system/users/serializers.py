from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

# 用户登录令牌序列化器
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义令牌获取序列化器，添加用户角色等信息
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # 添加用户自定义信息到token中
        token['username'] = user.username
        token['role'] = user.role
        token['kindergarten_id'] = user.kindergarten.id if user.kindergarten else None
        token['teacher_id'] = user.teacher.id if user.teacher else None
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # 添加用户信息到返回数据中
        data['username'] = self.user.username
        data['role'] = self.user.role
        data['name'] = self.user.first_name or self.user.username
        data['kindergarten'] = self.user.kindergarten.name if self.user.kindergarten else None
        data['kindergarten_id'] = self.user.kindergarten.id if self.user.kindergarten else None
        data['teacher_id'] = self.user.teacher.id if self.user.teacher else None
        
        # 教师需要返回关联的班级信息
        if self.user.is_teacher():
            data['classes'] = [{
                'id': cls.id,
                'name': cls.name
            } for cls in self.user.classes.all()]
        
        return data

# 用户简要信息序列化器
class UserBriefSerializer(serializers.ModelSerializer):
    """
    用户简要信息序列化器，用于关联字段的序列化
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'first_name', 'last_name']

# 用户序列化器
class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器，用于用户信息的序列化和反序列化
    """
    # 只读字段
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    
    # 关联字段
    kindergarten_name = serializers.SerializerMethodField(read_only=True)
    class_names = serializers.SerializerMethodField(read_only=True)
    teacher_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'first_name', 'last_name', 
            'role', 'kindergarten', 'kindergarten_name', 'classes', 'class_names',
            'teacher', 'teacher_name', 'phone', 'avatar',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'kindergarten': {'required': False},
            'classes': {'required': False},
            'teacher': {'required': False}
        }
    
    def to_internal_value(self, data):
        """
        反序列化输入时的处理
        """
        # 创建数据的副本以避免修改原始数据
        modified_data = data.copy()
        
        # 移除不需要的字段
        modified_data.pop('id', None)  # id 通常由数据库自动生成
        modified_data.pop('is_active', None)  # 移除状态字段
        
        # 调用父类方法处理
        return super().to_internal_value(modified_data)
    
    def to_representation(self, instance):
        """
        序列化输出时的处理
        """
        data = super().to_representation(instance)
        # 移除不需要的字段
        data.pop('is_active', None)
        return data
    
    def get_kindergarten_name(self, obj):
        """
        获取幼儿园名称
        """
        return obj.kindergarten.name if obj.kindergarten else None
    
    def get_class_names(self, obj):
        """
        获取关联的班级名称列表
        """
        return [cls.name for cls in obj.classes.all()]
    
    def get_teacher_name(self, obj):
        """
        获取关联的教师姓名
        """
        return obj.teacher.name if obj.teacher else None
    
    def create(self, validated_data):
        """
        创建用户时处理密码加密
        """
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        """
        更新用户时处理密码加密
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

# 用户注册序列化器
class UserRegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    """
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'first_name', 'phone', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'required': True}
        }
    
    def validate(self, attrs):
        """
        验证密码一致性
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("密码不匹配")
        return attrs
    
    def create(self, validated_data):
        """
        创建用户
        """
        validated_data.pop('password_confirm')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user