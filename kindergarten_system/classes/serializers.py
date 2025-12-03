from rest_framework import serializers
from .models import Class
from kindergartens.models import Kindergarten
from teachers.models import Teacher

class KindergartenSerializer(serializers.ModelSerializer):
    """
    幼儿园信息序列化器
    """
    class Meta:
        model = Kindergarten
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    """
    教师信息序列化器
    """
    class Meta:
        model = Teacher
        fields = '__all__'

class ClassSerializer(serializers.ModelSerializer):
    """
    班级信息序列化器
    """
    kindergarten = KindergartenSerializer(read_only=True)
    kindergarten_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Class
        fields = [
            'id', 'name', 'class_type', 'kindergarten', 'kindergarten_id',
            'classroom_location', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ClassBriefSerializer(serializers.ModelSerializer):
    """
    班级简要信息序列化器
    """
    class Meta:
        model = Class
        fields = ['id', 'name', 'class_type']

class ClassImportSerializer(serializers.Serializer):
    """
    班级批量导入序列化器
    """
    file = serializers.FileField(required=True)
    
    def validate_file(self, value):
        """
        验证文件格式
        """
        if not value.name.endswith('.xlsx') and not value.name.endswith('.xls'):
            raise serializers.ValidationError('仅支持Excel文件(.xlsx, .xls)')
        return value