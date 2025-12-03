from django.db import models
from django.utils import timezone

# 班级模型
class Class(models.Model):
    # 班班类型选择
    CLASS_TYPE_CHOICES = (
        ('nursery', '托儿所'),
        ('small', '小班'),
        ('middle', '中班'),
        ('large', '大班'),
        ('pre_school', '学前班'),
    )

    # 基本信息
    name = models.CharField(max_length=100, verbose_name='班级名称')
    class_type = models.CharField(
        max_length=20,
        choices=CLASS_TYPE_CHOICES,
        verbose_name='班级类型',
        default='small'
    )
    
    # 关联幼儿园
    kindergarten = models.ForeignKey(
        'kindergartens.Kindergarten',
        on_delete=models.CASCADE,
        verbose_name='所属幼儿园'
    )
    
    # 教室位置
    classroom_location = models.CharField(max_length=100, verbose_name='教室位置', blank=True, default='')
    
    description = models.TextField(blank=True, verbose_name='班级描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def __str__(self):
        return f"{self.kindergarten.name} - {self.name}"
    
    class Meta:
        verbose_name = '班级'
        verbose_name_plural = '班级'
        ordering = ['kindergarten', 'name']
        unique_together = ('kindergarten', 'name')  # 在同一幼儿园内班级名称唯一