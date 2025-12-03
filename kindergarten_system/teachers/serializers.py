from rest_framework import serializers
from .models import Teacher
from kindergartens.models import Kindergarten
from classes.models import Class
from django.db import IntegrityError

class KindergartenBriefSerializer(serializers.ModelSerializer):
    """
    幼儿园简要信息序列化器
    """
    class Meta:
        model = Kindergarten
        fields = ['id', 'name']

class ClassBriefSerializer(serializers.ModelSerializer):
    """
    班级简要信息序列化器
    """
    class Meta:
        model = Class
        fields = ['id', 'name', 'class_type']

class TeacherSerializer(serializers.ModelSerializer):
    """
    教师信息序列化器
    """
    kindergarten = KindergartenBriefSerializer(read_only=True)
    kindergarten_id = serializers.IntegerField(write_only=True, required=False)
    classes = ClassBriefSerializer(many=True, read_only=True)
    class_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='班级ID列表'
    )
    class_id = serializers.IntegerField(write_only=True, required=False)  # 单个班级ID
    position_display = serializers.CharField(source='get_position_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    
    # 动态计算字段
    class_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    is_principal_flag = serializers.SerializerMethodField()
    
    class Meta:
        model = Teacher
        fields = [
            'id', 'employee_id', 'name', 'gender', 'gender_display', 'position', 'position_display',
            'kindergarten', 'kindergarten_id', 'phone', 'email', 'id_card',
            'hire_date', 'photo', 'classes', 'class_ids', 'class_id', 'is_active', 'notes',
            'created_at', 'updated_at', 'class_count', 'student_count', 'is_principal_flag'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_class_count(self, obj):
        """
        获取教师负责的班级数量
        """
        return obj.get_class_count()
    
    def get_student_count(self, obj):
        """
        获取教师负责的学生数量
        """
        return obj.get_student_count()
    
    def get_is_principal_flag(self, obj):
        """
        判断是否为园长
        """
        return obj.is_principal()
    
    def to_internal_value(self, data):
        """
        在验证前处理数据
        """
        # 处理日期格式
        if 'hire_date' in data and data['hire_date']:
            hire_date = data['hire_date']
            # 如果是ISO格式的日期时间字符串，只取日期部分
            if isinstance(hire_date, str) and 'T' in hire_date:
                data['hire_date'] = hire_date.split('T')[0]
        
        # 处理空字符串的电话号码
        if 'phone' in data and data['phone'] == '':
            data['phone'] = None
        
        # 处理空字符串的身份证号
        if 'id_card' in data and data['id_card'] == '':
            data['id_card'] = None
            
        return super().to_internal_value(data)
    
    def validate(self, data):
        """
        验证数据
        """
        # 处理班级ID，如果有单个班级ID，则转换为班级ID列表
        class_id = data.get('class_id')
        class_ids = data.get('class_ids', [])
        if class_id and class_id not in class_ids:
            class_ids.append(class_id)
            data['class_ids'] = class_ids
        
        # 如果有班级ID，通过第一个班级获取幼儿园ID
        if class_ids:
            try:
                from classes.models import Class
                first_class = Class.objects.get(id=class_ids[0])
                data['kindergarten_id'] = first_class.kindergarten_id
            except Class.DoesNotExist:
                raise serializers.ValidationError({'class_id': '班级不存在'})
        
        # 验证幼儿园是否存在（仅在提供了幼儿园ID时验证）
        kindergarten_id = data.get('kindergarten_id')
        if kindergarten_id is not None:
            try:
                Kindergarten.objects.get(id=kindergarten_id)
            except Kindergarten.DoesNotExist:
                raise serializers.ValidationError({'kindergarten_id': '幼儿园不存在'})
        
        # 验证手机号格式（仅在提供了手机号时验证）
        phone = data.get('phone')
        if phone:
            if not phone.isdigit() or len(phone) != 11:
                raise serializers.ValidationError({'phone': '手机号格式不正确'})
        
        # 验证身份证号格式（仅在提供了身份证号时验证）
        id_card = data.get('id_card')
        if id_card and len(id_card) != 18:
            raise serializers.ValidationError({'id_card': '身份证号格式不正确'})
        
        # 检查手机号唯一性（仅在提供了手机号且不为空时验证）
        if phone:
            # 获取当前实例（如果是更新操作）
            instance = self.instance
            if instance:
                # 如果是更新操作，检查手机号是否已更改
                if instance.phone != phone:
                    # 手机号已更改，检查新手机号是否已被使用
                    if Teacher.objects.filter(phone=phone).exclude(pk=instance.pk).exists():
                        raise serializers.ValidationError({'phone': '该手机号已被使用'})
            else:
                # 创建新教师，检查手机号是否已被使用
                if Teacher.objects.filter(phone=phone).exists():
                    raise serializers.ValidationError({'phone': '该手机号已被使用'})
        
        # 检查身份证号唯一性（仅在提供了身份证号且不为空时验证）
        if id_card:
            # 获取当前实例（如果是更新操作）
            instance = self.instance
            if instance:
                # 如果是更新操作，检查身份证号是否已更改
                if instance.id_card != id_card:
                    # 身份证号已更改，检查新身份证号是否已被使用
                    if Teacher.objects.filter(id_card=id_card).exclude(pk=instance.pk).exists():
                        raise serializers.ValidationError({'id_card': '该身份证号已被使用'})
            else:
                # 创建新教师，检查身份证号是否已被使用
                if Teacher.objects.filter(id_card=id_card).exists():
                    raise serializers.ValidationError({'id_card': '该身份证号已被使用'})

        return data
    
    def create(self, validated_data):
        """
        创建教师
        """
        # 提取班级ID
        class_ids = validated_data.pop('class_ids', [])
        # 移除class_id，因为它不是Teacher模型的字段
        validated_data.pop('class_id', None)
        
        # 如果没有提供kindergarten_id，使用当前用户的幼儿园
        request = self.context.get('request')
        if request and hasattr(request.user, 'kindergarten') and not validated_data.get('kindergarten_id'):
            validated_data['kindergarten_id'] = request.user.kindergarten.id
        
        try:
            # 创建教师
            teacher = Teacher.objects.create(**validated_data)
            
            # 添加班级关联
            if class_ids:
                classes = Class.objects.filter(id__in=class_ids, kindergarten_id=teacher.kindergarten_id)
                teacher.classes.set(classes)
            
            return teacher
        except IntegrityError as e:
            # 捕获唯一性约束错误并转换为验证错误
            if 'phone' in str(e):
                raise serializers.ValidationError({'phone': '该手机号已被使用'})
            elif 'id_card' in str(e):
                raise serializers.ValidationError({'id_card': '该身份证号已被使用'})
            else:
                raise serializers.ValidationError('创建教师时发生错误')
    
    def update(self, instance, validated_data):
        """
        更新教师信息
        """
        # 提取班级ID
        class_ids = validated_data.pop('class_ids', None)
        
        try:
            # 更新基本信息
            for field, value in validated_data.items():
                setattr(instance, field, value)
            instance.save()
            
            # 更新班级关联
            if class_ids is not None:
                classes = Class.objects.filter(id__in=class_ids, kindergarten_id=instance.kindergarten_id)
                instance.classes.set(classes)
            
            return instance
        except IntegrityError as e:
            # 捕获唯一性约束错误并转换为验证错误
            if 'phone' in str(e):
                raise serializers.ValidationError({'phone': '该手机号已被使用'})
            elif 'id_card' in str(e):
                raise serializers.ValidationError({'id_card': '该身份证号已被使用'})
            else:
                raise serializers.ValidationError('更新教师时发生错误')

class TeacherBriefSerializer(serializers.ModelSerializer):
    """
    教师简要信息序列化器
    """
    position_display = serializers.CharField(source='get_position_display')
    
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'position', 'position_display']

class TeacherImportSerializer(serializers.Serializer):
    """
    教师批量导入序列化器
    """
    file = serializers.FileField(required=True)
    
    def validate_file(self, value):
        """
        验证文件格式
        """
        if not value.name.endswith('.xlsx') and not value.name.endswith('.xls'):
            raise serializers.ValidationError('仅支持Excel文件(.xlsx, .xls)')
        return value

class TeacherStatsSerializer(serializers.Serializer):
    """
    教师统计信息序列化器
    """
    total_count = serializers.IntegerField()
    active_count = serializers.IntegerField()
    inactive_count = serializers.IntegerField()
    position_stats = serializers.ListField(child=serializers.DictField())
    gender_stats = serializers.ListField(child=serializers.DictField())
    avg_teachers_per_kindergarten = serializers.FloatField()
    avg_students_per_teacher = serializers.FloatField()
    teacher_with_most_classes = serializers.DictField(allow_null=True)
    teacher_with_most_students = serializers.DictField(allow_null=True)
    recent_hires_count = serializers.IntegerField()
    long_term_teachers_count = serializers.IntegerField()