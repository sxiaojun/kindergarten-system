from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

# 教师模型
class Teacher(models.Model):
    """
    教师信息模型，存储幼儿园教师的基本信息
    """
    # 教师职务
    POSITION_CHOICES = [
        ('headmaster', '园长'),
        ('deputy_headmaster', '副园长'),
        ('head_teacher', '班主任'),
        ('assistant_teacher', '配班老师'),
        ('life_teacher', '生活老师'),
        ('principal', '园长'),
        ('teacher', '教师'),
        ('assistant', '助教'),
    ]
    
    # 基本信息
    name = models.CharField(
        '教师姓名', 
        max_length=50,
        help_text='请输入教师姓名'
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
        default='female'
    )
    
    # 关联的幼儿园
    kindergarten = models.ForeignKey(
        'kindergartens.Kindergarten', 
        on_delete=models.CASCADE,
        related_name='teachers',
        verbose_name='所属幼儿园'
    )
    
    # 职务信息
    position = models.CharField(
        '职务', 
        max_length=30, 
        choices=POSITION_CHOICES,
        default='teacher'
    )
    
    # 联系信息
    employee_id = models.CharField(
        '工号', 
        max_length=30,
        null=True,
        blank=True,
        help_text='请输入教师工号'
    )
    
    phone = models.CharField(
        '手机号', 
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        help_text='请输入教师手机号'
    )

    email = models.EmailField(
        '电子邮箱', 
        max_length=100,
        blank=True,
        null=True
    )
    
    # 证件信息
    id_card = models.CharField(
        '身份证号', 
        max_length=18,
        unique=True,
        null=True,
        blank=True,
        help_text='请输入教师身份证号'
    )
    
    # 工作信息
    hire_date = models.DateField(
        '入职日期', 
        blank=True,
        null=True
    )
    
    # 照片
    photo = models.ImageField(
        '教师照片', 
        upload_to='teacher_photos/', 
        blank=True,
        null=True
    )
    
    # 关联的班级（多对多）
    classes = models.ManyToManyField(
        'classes.Class', 
        blank=True,
        related_name='teachers',
        verbose_name='负责班级'
    )
    
    # 状态
    is_active = models.BooleanField(
        '是否在职', 
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
        verbose_name = '教师'
        verbose_name_plural = '教师管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name}({self.get_position_display()})'
    
    def clean(self):
        # 在验证阶段检查电话号码
        if self.phone == "":
            self.phone = None
            
        # 检查身份证号码
        if self.id_card == "":
            self.id_card = None
    
    def save(self, *args, **kwargs):
        """
        重写save方法，确保在更新时不违反唯一性约束
        """
        # 清理空字符串
        self.clean()
        
        # 检查是否是更新操作
        if self.pk:
            # 获取原始对象
            original = Teacher.objects.get(pk=self.pk)
            # 如果phone没有改变，则跳过唯一性检查
            if original.phone != self.phone:
                # 只有当手机号改变时才检查唯一性
                if self.phone and Teacher.objects.filter(phone=self.phone).exclude(pk=self.pk).exists():
                    raise ValidationError({'phone': '该手机号已被使用'})
            
            # 如果id_card没有改变，则跳过唯一性检查
            if original.id_card != self.id_card:
                # 只有当身份证号改变时才检查唯一性
                if self.id_card and Teacher.objects.filter(id_card=self.id_card).exclude(pk=self.pk).exists():
                    raise ValidationError({'id_card': '该身份证号已被使用'})
        else:
            # 创建新对象时检查唯一性
            if self.phone and Teacher.objects.filter(phone=self.phone).exists():
                raise ValidationError({'phone': '该手机号已被使用'})
                
            if self.id_card and Teacher.objects.filter(id_card=self.id_card).exists():
                raise ValidationError({'id_card': '该身份证号已被使用'})
        
        super().save(*args, **kwargs)
    
    # 判断是否为园长
    def is_principal(self):
        """
        判断是否为园长
        """
        return self.position in ['headmaster', 'deputy_headmaster']
    
    # 获取教师负责的班级数量
    def get_class_count(self):
        """
        获取教师负责的班级数量
        """
        return self.classes.count()
    
    # 获取教师负责的学生数量
    def get_student_count(self):
        """
        获取教师负责的学生数量
        """
        from children.models import Child
        # 获取教师所有负责班级的学生总数
        student_count = 0
        for class_info in self.classes.all():
            student_count += Child.objects.filter(class_info=class_info, is_active=True).count()
        return student_count
    
    # 获取教师负责的班级（用于兼容teaching_classes属性）
    @property
    def teaching_classes(self):
        """
        获取教师负责的班级，用于兼容旧代码
        """
        return self.classes