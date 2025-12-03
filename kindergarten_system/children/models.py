from django.db import models
from django.utils import timezone

# 幼儿模型
class Child(models.Model):
    """
    幼儿信息模型，存储幼儿园学生的基本信息
    """
    # 基本信息
    name = models.CharField(
        '幼儿姓名', 
        max_length=50,
        help_text='请输入幼儿姓名'
    )
    
    # 性别
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
    ]
    gender = models.CharField(
        '性别', 
        max_length=10, 
        choices=GENDER_CHOICES,
        default='male'
    )
    
    # 出生日期
    birth_date = models.DateField(
        '出生日期',
        blank=True,
        null=True,
        help_text='请选择幼儿出生日期'
    )
    
    # 关联的班级
    class_info = models.ForeignKey(
        'classes.Class', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='所属班级'
    )
    
    # 学号
    student_id = models.CharField(
        '学号', 
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        help_text='请输入幼儿学号'
    )
    
    # 入园日期
    admission_date = models.DateField(
        '入园日期',
        blank=True,
        null=True,
        help_text='请选择幼儿入园日期'
    )
    
    # 联系信息
    parent_name = models.CharField(
        '家长姓名', 
        max_length=50,
        blank=True,
        null=True,
        help_text='请输入家长姓名'
    )
    
    parent_phone = models.CharField(
        '家长手机号', 
        max_length=11,
        blank=True,
        null=True,
        help_text='请输入家长手机号'
    )
    
    parent_email = models.EmailField(
        '家长邮箱', 
        max_length=100,
        blank=True,
        null=True
    )
    
    # 家庭地址
    home_address = models.CharField(
        '家庭地址', 
        max_length=255,
        blank=True,
        null=True
    )
    
    # 幼儿头像
    avatar = models.ImageField(
        '幼儿头像', 
        upload_to='child_avatars/',
        blank=True,
        null=True
    )
    
    # 健康信息
    health_notes = models.TextField(
        '健康备注', 
        blank=True,
        null=True,
        help_text='过敏史、特殊疾病等健康相关信息'
    )
    
    # 状态
    is_active = models.BooleanField(
        '是否在读', 
        default=True
    )
    
    # 备注
    notes = models.TextField(
        '备注', 
        blank=True,
        null=True
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
        verbose_name = '幼儿'
        verbose_name_plural = '幼儿管理'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.class_info:
            return f'{self.class_info.kindergarten.name} - {self.class_info.name} - {self.name}'
        return self.name
    
    # 计算年龄
    def get_age(self):
        """
        计算幼儿当前年龄
        """
        if self.birth_date:
            today = timezone.now().date()
            age = today.year - self.birth_date.year
            # 如果还没过生日，年龄减1
            if today.month < self.birth_date.month or (
                today.month == self.birth_date.month and today.day < self.birth_date.day
            ):
                age -= 1
            return age
        return None
    
    # 获取幼儿所在的幼儿园
    def get_kindergarten(self):
        """
        获取幼儿所在的幼儿园
        """
        if self.class_info:
            return self.class_info.kindergarten
        return None
    
    # 获取幼儿的选区记录数
    def get_selection_count(self):
        """
        获取幼儿的选区记录数
        """
        from selections.models import SelectionRecord
        return SelectionRecord.objects.filter(child=self).count()
