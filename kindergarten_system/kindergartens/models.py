from django.db import models
from django.utils import timezone

# 幼儿园模型
class Kindergarten(models.Model):
    """
    幼儿园信息模型，存储幼儿园的基本信息
    """
    # 基本信息
    name = models.CharField(
        '幼儿园名称', 
        max_length=100, 
        unique=True,  # 幼儿园名称唯一
        help_text='请输入幼儿园全称'
    )
    
    # 园所类型
    TYPE_CHOICES = [
        ('public', '公立'),
        ('private', '私立'),
        ('chain', '连锁'),
    ]
    kindergarten_type = models.CharField(
        '园所类型', 
        max_length=20, 
        choices=TYPE_CHOICES,
        default='private'
    )
    
    # 联系信息
    address = models.CharField(
        '详细地址', 
        max_length=255,
        blank=True,
        null=True,
        help_text='请输入幼儿园的详细地址'
    )
    phone = models.CharField(
        '联系电话', 
        max_length=20,
        blank=True,
        null=True
    )
    
    # 负责人
    principal_name = models.CharField(
        '园长姓名', 
        max_length=50,
        blank=True,
        null=True
    )
    
    # 地区
    region = models.CharField(
        '地区',
        max_length=100,
        blank=True,
        null=True,
        help_text='请输入幼儿园所在地区'
    )
    
    # 规模信息
    total_students = models.IntegerField(
        '学生总数', 
        default=0,
        help_text='幼儿园学生总数'
    )
    total_classes = models.IntegerField(
        '班级总数', 
        default=0,
        help_text='幼儿园班级总数'
    )
    total_teachers = models.IntegerField(
        '教师总数', 
        default=0,
        help_text='幼儿园教师总数'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        '创建时间', 
        default=timezone.now
    )
    updated_at = models.DateTimeField(
        '更新时间', 
        auto_now=True
    )
    
    class Meta:
        verbose_name = '幼儿园'
        verbose_name_plural = '幼儿园管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    # 统计班级数量（动态计算）
    def get_class_count(self):
        """
        获取该幼儿园的班级数量
        """
        try:
            from classes.models import Class
            return Class.objects.filter(kindergarten=self).count()
        except (ImportError, AttributeError):
            return 0
    
    # 统计学生数量（动态计算）
    def get_student_count(self):
        """
        获取该幼儿园的学生数量
        """
        try:
            from children.models import Child
            return Child.objects.filter(class_info__kindergarten=self, is_active=True).count()
        except (ImportError, AttributeError):
            return 0
    
    # 统计教师数量（动态计算）
    def get_teacher_count(self):
        """
        获取该幼儿园的教师数量
        """
        try:
            from teachers.models import Teacher
            return Teacher.objects.filter(kindergarten=self, is_active=True).count()
        except (ImportError, AttributeError):
            return 0
