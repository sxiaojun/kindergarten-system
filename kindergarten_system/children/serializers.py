from rest_framework import serializers
from .models import Child
from classes.serializers import ClassBriefSerializer
from kindergartens.serializers import KindergartenBriefSerializer

class ChildSerializer(serializers.ModelSerializer):
    """
    幼儿信息序列化器
    """
    # 关联字段
    class_info = ClassBriefSerializer(read_only=True)
    class_id = serializers.IntegerField(write_only=True, required=False)
    kindergarten = KindergartenBriefSerializer(read_only=True)
    
    # 动态计算字段
    age = serializers.SerializerMethodField(read_only=True)
    selection_count = serializers.SerializerMethodField(read_only=True)
    class_name = serializers.SerializerMethodField(read_only=True)
    
    # 适配前端字段名
    enroll_date = serializers.DateField(source='admission_date', required=False)

    # 头像字段
    avatar = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Child
        fields = [
            'id', 'name', 'gender', 'birth_date', 'age',
            'class_info', 'class_id', 'kindergarten', 'student_id',
            'admission_date', 'enroll_date', 'parent_name', 'parent_phone',
            'parent_email', 'home_address', 'avatar', 'health_notes',
            'notes', 'selection_count',  # 删除 is_active 和 status 字段
            'class_name',  # 添加class_name字段
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_age(self, obj):
        """
        获取幼儿年龄
        """
        return obj.get_age()
    
    def get_selection_count(self, obj):
        """
        获取幼儿的选区记录数
        """
        return obj.get_selection_count()
    
    def get_status(self, obj):
        """
        将is_active转换为前端期望的status格式
        """
        return 'active' if obj.is_active else 'inactive'
    
    def get_class_name(self, obj):
        """
        获取班级名称
        """
        return obj.class_info.name if obj.class_info else None
    
    def validate(self, data):
        """
        验证数据
        """
        # 只验证必填字段（根据需求：姓名、性别、班级）
        if not data.get('name'):
            raise serializers.ValidationError({"name": "幼儿姓名不能为空"})
        
        if not data.get('gender'):
            raise serializers.ValidationError({"gender": "性别不能为空"})
        
        # 验证班级
        class_id = data.get('class_id')
        if not class_id:
            raise serializers.ValidationError({"class_id": "班级不能为空"})
        
        return data
    
    def create(self, validated_data):
        """
        创建幼儿记录
        """
        # 处理班级关联
        if 'class_id' in validated_data:
            class_id = validated_data.pop('class_id')
            if class_id:
                from classes.models import Class
                try:
                    class_obj = Class.objects.get(id=class_id)
                    validated_data['class_info'] = class_obj
                except Class.DoesNotExist:
                    raise serializers.ValidationError({"class_id": "指定的班级不存在"})
        
        # 不移除avatar字段，允许在创建时处理头像
        
        # 如果没有提供入园日期，默认设为今天
        if 'admission_date' not in validated_data:
            validated_data['admission_date'] = timezone.now().date()
        
        # 如果没有提供出生日期，默认设为今天
        if 'birth_date' not in validated_data or validated_data.get('birth_date') is None:
            validated_data['birth_date'] = timezone.now().date()
        
        # 如果没有提供家长姓名，设置为空字符串而不是None
        if 'parent_name' not in validated_data or validated_data.get('parent_name') is None:
            validated_data['parent_name'] = ''
        
        # 如果没有提供家长手机号，设置为空字符串而不是None
        if 'parent_phone' not in validated_data or validated_data.get('parent_phone') is None:
            validated_data['parent_phone'] = ''
        
        # 创建幼儿记录
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        更新幼儿记录
        """
        # 处理班级关联
        if 'class_id' in validated_data:
            class_id = validated_data.pop('class_id')
            if class_id:
                from classes.models import Class
                try:
                    class_obj = Class.objects.get(id=class_id)
                    instance.class_info = class_obj
                except Class.DoesNotExist:
                    raise serializers.ValidationError({"class_id": "指定的班级不存在"})
            else:
                instance.class_info = None
        
        # 不移除avatar字段，允许在更新时处理头像
        
        # 更新其他字段
        return super().update(instance, validated_data)

class ChildBriefSerializer(serializers.ModelSerializer):
    """
    幼儿简要信息序列化器（用于关联字段）
    """
    class Meta:
        model = Child
        fields = ['id', 'name', 'gender', 'age']
    
    def get_age(self, obj):
        """
        获取幼儿年龄
        """
        return obj.get_age()



class ChildFilterSerializer(serializers.Serializer):
    """
    幼儿筛选参数序列化器
    """
    name = serializers.CharField(required=False, allow_blank=True)
    class_id = serializers.IntegerField(required=False)
    parent_name = serializers.CharField(required=False, allow_blank=True)
    parent_phone = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=['active', 'inactive'],
        required=False,
        allow_null=True
    )
    kindergarten_id = serializers.IntegerField(required=False)
    date_start = serializers.DateField(required=False)
    date_end = serializers.DateField(required=False)
class ChildImportSerializer(serializers.Serializer):
    """
    幼儿批量导入序列化器
    """
    file = serializers.FileField(required=True)
    
    def validate_file(self, value):
        """
        验证导入文件
        """
        import os
        from django.core.exceptions import ValidationError
        
        # 验证文件类型
        ext = os.path.splitext(value.name)[1]
        valid_extensions = ['.xlsx', '.xls']
        if ext.lower() not in valid_extensions:
            raise ValidationError("只支持Excel文件格式（.xlsx, .xls）")
        
        return value

from django.utils import timezone