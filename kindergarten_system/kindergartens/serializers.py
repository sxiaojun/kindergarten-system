from rest_framework import serializers
from .models import Kindergarten

# 幼儿园序列化器
class KindergartenSerializer(serializers.ModelSerializer):
    """
    幼儿园序列化器，用于幼儿园信息的序列化和反序列化
    """
    # 只读字段
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    
    # 动态计算字段
    class_count = serializers.SerializerMethodField(read_only=True)
    student_count = serializers.SerializerMethodField(read_only=True)
    teacher_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Kindergarten
        fields = [
            'id', 'name', 'kindergarten_type', 'address', 'principal_name',
            'phone', 'region', 'total_students', 'total_teachers', 'total_classes',
            'class_count', 'student_count', 'teacher_count', 
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'kindergarten_type': {'default': 'private'},
            'total_students': {'default': 0},
            'total_teachers': {'default': 0},
            'total_classes': {'default': 0},
        }
    
    def get_class_count(self, obj):
        """
        获取班级数量
        """
        return obj.get_class_count()
    
    def get_student_count(self, obj):
        """
        获取学生数量
        """
        return obj.get_student_count()
    
    def get_teacher_count(self, obj):
        """
        获取教师数量
        """
        return obj.get_teacher_count()
    
    def to_representation(self, instance):
        """
        序列化输出时的处理
        """
        data = super().to_representation(instance)
        # 将 principal_name 映射为 contact_person 输出
        data['contact_person'] = data.get('principal_name', '')
        # 将 phone 映射为 contact_phone 输出
        data['contact_phone'] = data.get('phone', '')
        return data
    
    def to_internal_value(self, data):
        """
        反序列化输入时的处理
        """
        # 创建数据的副本以避免修改原始数据
        modified_data = data.copy()
        
        # 处理字段映射
        if 'contact_person' in modified_data:
            modified_data['principal_name'] = modified_data.pop('contact_person')
        if 'contact_phone' in modified_data:
            modified_data['phone'] = modified_data.pop('contact_phone')
        
        # 移除不需要的字段
        modified_data.pop('id', None)  # id 通常由数据库自动生成
        modified_data.pop('status', None)  # 移除状态字段
        
        # 调用父类方法处理
        return super().to_internal_value(modified_data)

# 幼儿园简要信息序列化器（用于关联字段）
class KindergartenBriefSerializer(serializers.ModelSerializer):
    """
    幼儿园简要信息序列化器，用于其他模型的关联字段
    """
    class Meta:
        model = Kindergarten
        fields = ['id', 'name', 'kindergarten_type']

# 幼儿园批量导入序列化器
class KindergartenImportSerializer(serializers.Serializer):
    """
    幼儿园批量导入序列化器
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