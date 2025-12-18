from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import SelectionArea, SelectionRecord
from children.models import Child
from classes.models import Class
from users.models import User
from django.utils import timezone
from datetime import date

class SelectionAreaSerializer(serializers.ModelSerializer):
    """
    选区定义序列化器
    """
    # 关联字段
    class_name = serializers.CharField(source='class_info.name', read_only=True)
    kindergarten_name = serializers.CharField(source='class_info.kindergarten.name', read_only=True)
    class_id = serializers.IntegerField(write_only=True, required=False)
    image = serializers.ImageField(required=False, allow_null=True)
    current_selections = serializers.SerializerMethodField()
    
    class Meta:
        model = SelectionArea
        fields = [
            'id', 'name', 'class_id', 'class_name', 'kindergarten_name',
            'max_selections', 'description', 'image', 'created_at', 'updated_at', 'current_selections'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'class_name', 'kindergarten_name']

    def get_current_selections(self, obj):
        """
        获取该选区当天已选择的人数
        """
        today = timezone.now().date()
        return SelectionRecord.objects.filter(
            selection_area=obj,
            date=today,
            is_active=True
        ).count()

    def validate_class_id(self, value):
        """
        验证班级ID的有效性
        """
        if value:
            try:
                Class.objects.get(id=value)
                return value
            except Class.DoesNotExist:
                raise serializers.ValidationError('指定的班级不存在')
        return value
    
    def create(self, validated_data):
        # 使用class_id创建class_info关联
        if 'class_id' in validated_data and validated_data['class_id']:
            class_obj = Class.objects.get(id=validated_data.pop('class_id'))
            validated_data['class_info'] = class_obj
        instance = super().create(validated_data)
        return instance
    
    def update(self, instance, validated_data):
        # 使用class_id更新class_info关联
        if 'class_id' in validated_data and validated_data['class_id']:
            class_obj = Class.objects.get(id=validated_data.pop('class_id'))
            validated_data['class_info'] = class_obj
        try:
            instance = super().update(instance, validated_data)
        except ValidationError as e:
            # 检查是否是唯一性约束错误
            error_str = str(e).lower()
            if 'unique constraint' in error_str or 'unique_together' in error_str:
                raise serializers.ValidationError('包含选区名称和所属班级的选区定义已经存在')
            raise
        return instance
    
    def to_representation(self, instance):
        """
        重写序列化输出，添加class_id字段
        """
        data = super().to_representation(instance)
        if hasattr(instance, 'class_info'):
            data['class_id'] = instance.class_info.id
        # 如果有图片，返回图片的完整URL
        if instance.image:
            request = self.context.get('request')
            if request:
                data['image'] = request.build_absolute_uri(instance.image.url)
        return data

class SelectionAreaBriefSerializer(serializers.ModelSerializer):
    """
    选区简要信息序列化器，用于下拉选择等场景
    """
    class Meta:
        model = SelectionArea
        fields = ['id', 'name', 'class_info', 'class_id']
        read_only_fields = ['id', 'name', 'class_info', 'class_id']

class SelectionRecordSerializer(serializers.ModelSerializer):
    """
    选区记录序列化器
    """
    # 关联字段
    child_name = serializers.CharField(source='child.name', read_only=True)
    child_gender = serializers.CharField(source='child.gender', read_only=True)
    child_age = serializers.SerializerMethodField()
    child_class = serializers.CharField(source='child.class_info.name', read_only=True)
    selection_area_name = serializers.CharField(source='selection_area.name', read_only=True)
    class_name = serializers.CharField(source='selection_area.class_info.name', read_only=True)
    kindergarten_name = serializers.CharField(source='selection_area.class_info.kindergarten.name', read_only=True)
    operated_by_name = serializers.CharField(source='operated_by.username', read_only=True)
    
    class Meta:
        model = SelectionRecord
        fields = [
            'id', 'child', 'child_name', 'child_gender', 'child_age', 'child_class',
            'selection_area', 'selection_area_name', 'class_name', 'kindergarten_name',
            'date', 'select_time', 'operated_by', 'operated_by_name', 'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_child_age(self, obj):
        """
        获取幼儿年龄
        """
        return obj.child.get_age()
    
    def validate(self, data):
        """
        验证选区记录的有效性
        """
        # 确保幼儿和选区存在
        if 'child' in data:
            try:
                Child.objects.get(id=data['child'].id)
            except Child.DoesNotExist:
                raise serializers.ValidationError({'child': '指定的幼儿不存在'})
        
        if 'selection_area' in data:
            try:
                SelectionArea.objects.get(id=data['selection_area'].id)
            except SelectionArea.DoesNotExist:
                raise serializers.ValidationError({'selection_area': '指定的选区不存在'})
        
        # 确保幼儿和选区属于同一个班级
        if 'child' in data and 'selection_area' in data:
            if data['child'].class_info != data['selection_area'].class_info:
                raise serializers.ValidationError('幼儿和选区不属于同一个班级')
        
        return data

class SelectionRecordCreateSerializer(serializers.ModelSerializer):
    """
    创建选区记录的专用序列化器
    """
    # 允许通过ID创建记录
    child_id = serializers.IntegerField(write_only=True)
    selection_area_id = serializers.IntegerField(write_only=True)
    select_time = serializers.DateTimeField(required=False)
    
    class Meta:
        model = SelectionRecord
        fields = [
            'child_id', 'selection_area_id', 'select_time', 'date', 'notes', 'operated_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'date']
    
    def validate_child_id(self, value):
        """
        验证幼儿ID的有效性
        """
        try:
            Child.objects.get(id=value)
            return value
        except Child.DoesNotExist:
            raise serializers.ValidationError('指定的幼儿不存在')
    
    def validate_selection_area_id(self, value):
        """
        验证选区ID的有效性
        """
        try:
            SelectionArea.objects.get(id=value)
            return value
        except SelectionArea.DoesNotExist:
            raise serializers.ValidationError('指定的选区不存在')
    
    def create(self, validated_data):
        """
        创建选区记录
        """
        # 获取关联的对象
        child = Child.objects.get(id=validated_data.pop('child_id'))
        selection_area = SelectionArea.objects.get(id=validated_data.pop('selection_area_id'))
        
        # 验证幼儿和选区属于同一个班级
        if child.class_info != selection_area.class_info:
            raise serializers.ValidationError('幼儿和选区不属于同一个班级')
        
        # 设置选择时间
        select_time = validated_data.get('select_time') or timezone.now()
        
        # 从选择时间中提取日期
        record_date = select_time.date()
        
        # 检查是否已存在该幼儿在该日期的记录
        try:
            existing_record = SelectionRecord.objects.get(
                child=child,
                date=record_date
            )
            # 如果存在，更新现有记录而不是创建新记录
            existing_record.selection_area = selection_area
            existing_record.select_time = select_time
            existing_record.is_active = True
            existing_record.notes = validated_data.get('notes', existing_record.notes)
            existing_record.operated_by = validated_data.get('operated_by', existing_record.operated_by)
            existing_record.updated_at = timezone.now()
            existing_record.save()
            return existing_record
        except SelectionRecord.DoesNotExist:
            # 如果不存在，创建新记录
            validated_data['date'] = record_date
            validated_data['child'] = child
            validated_data['selection_area'] = selection_area
            validated_data['is_active'] = True
            validated_data['select_time'] = select_time
            
            return super().create(validated_data)


class SelectionRecordUpdateSerializer(serializers.ModelSerializer):
    """
    更新选区记录的专用序列化器
    """
    # 允许通过ID更新记录
    child_id = serializers.IntegerField(write_only=True, required=False)
    selection_area_id = serializers.IntegerField(write_only=True, required=False)
    select_time = serializers.DateTimeField(required=False)
    
    class Meta:
        model = SelectionRecord
        fields = [
            'child_id', 'selection_area_id', 'select_time', 'date', 'notes', 'operated_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'date']
    
    def validate_child_id(self, value):
        """
        验证幼儿ID的有效性
        """
        try:
            Child.objects.get(id=value)
            return value
        except Child.DoesNotExist:
            raise serializers.ValidationError('指定的幼儿不存在')
    
    def validate_selection_area_id(self, value):
        """
        验证选区ID的有效性
        """
        try:
            SelectionArea.objects.get(id=value)
            return value
        except SelectionArea.DoesNotExist:
            raise serializers.ValidationError('指定的选区不存在')
    
    def update(self, instance, validated_data):
        """
        更新选区记录
        """
        # 处理关联的对象
        if 'child_id' in validated_data:
            child = Child.objects.get(id=validated_data.pop('child_id'))
            validated_data['child'] = child
        
        if 'selection_area_id' in validated_data:
            selection_area = SelectionArea.objects.get(id=validated_data.pop('selection_area_id'))
            validated_data['selection_area'] = selection_area
            
        # 验证幼儿和选区属于同一个班级
        child = validated_data.get('child', instance.child)
        selection_area = validated_data.get('selection_area', instance.selection_area)
        if child.class_info != selection_area.class_info:
            raise serializers.ValidationError('幼儿和选区不属于同一个班级')
        
        # 处理选择时间
        if 'select_time' in validated_data:
            select_time = validated_data['select_time']
            # 从选择时间中提取日期并设置date字段
            validated_data['date'] = select_time.date()
        
        return super().update(instance, validated_data)

class SelectionFilterSerializer(serializers.Serializer):
    """
    选区记录筛选序列化器
    """
    class_id = serializers.IntegerField(required=False)
    kindergarten_id = serializers.IntegerField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    child_name = serializers.CharField(required=False, max_length=100)
    selection_area_id = serializers.IntegerField(required=False)
    is_active = serializers.BooleanField(required=False)
    operated_by = serializers.IntegerField(required=False)
    
    def validate(self, data):
        """
        验证筛选条件的有效性
        """
        # 验证日期范围
        if 'date_from' in data and 'date_to' in data:
            if data['date_from'] > data['date_to']:
                raise serializers.ValidationError('开始日期不能晚于结束日期')
        
        return data

class SelectionStatisticsSerializer(serializers.Serializer):
    """
    选区统计序列化器
    """
    class_id = serializers.IntegerField(required=False)
    kindergarten_id = serializers.IntegerField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    group_by = serializers.ChoiceField(
        choices=['date', 'selection_area', 'child', 'class'],
        default='date'
    )
    
    def validate(self, data):
        """
        验证统计条件的有效性
        """
        # 验证日期范围
        if 'date_from' in data and 'date_to' in data:
            if data['date_from'] > data['date_to']:
                raise serializers.ValidationError('开始日期不能晚于结束日期')
        
        return data
