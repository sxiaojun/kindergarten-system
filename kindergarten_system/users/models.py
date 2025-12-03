from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# 自定义用户模型
class User(AbstractUser):
    """
    用户模型，继承自AbstractUser，扩展了幼儿园管理系统所需的字段
    """
    # 权限类型
    ROLE_CHOICES = [
        ('owner', '系统所有者'),  # 拥有所有模块数据权限
        ('principal', '园长'),    # 拥有本幼儿园所有数据权限
        ('teacher', '教师'),      # 拥有关联班级和选区数据权限
    ]
    
    # 扩展字段
    role = models.CharField(
        '权限角色', 
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='teacher'
    )
    
    # 关联的幼儿园（教师和园长需要关联）
    kindergarten = models.ForeignKey(
        'kindergartens.Kindergarten', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='所属幼儿园'
    )
    
    # 关联的班级（教师需要关联）
    classes = models.ManyToManyField(
        'classes.Class', 
        blank=True,
        verbose_name='关联班级'
    )
    
    # 关联的教师记录（当用户角色为教师时）
    teacher = models.OneToOneField(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='关联教师'
    )
    
    # 联系信息
    phone = models.CharField(
        '手机号', 
        max_length=11, 
        blank=True,
        null=True
    )
    
    # 头像
    avatar = models.ImageField(
        '头像', 
        upload_to='avatars/', 
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
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.username}({self.get_role_display()})'
    
    # 判断是否为系统所有者
    def is_owner(self):
        return self.role == 'owner'
    
    # 判断是否为园长
    def is_principal(self):
        return self.role == 'principal'
    
    # 判断是否为教师
    def is_teacher(self):
        return self.role == 'teacher'