from django.db import models
from django.utils import timezone
from classes.models import Class

class SelectionArea(models.Model):
    """
    选区定义模型
    用于定义各个班级中的不同活动区域
    """
    # 选区名称
    name = models.CharField(
        '选区名称', 
        max_length=100,
        help_text='请输入选区名称，如阅读区、建构区等'
    )
    
    # 关联的班级
    class_info = models.ForeignKey(
        'classes.Class', 
        on_delete=models.CASCADE,
        related_name='selection_areas',
        verbose_name='所属班级'
    )
    
    # 描述信息
    description = models.TextField(
        '选区描述', 
        blank=True,
        null=True,
        help_text='选区的详细描述信息'
    )
    
    # 选区图片
    image = models.ImageField(
        '选区图片',
        upload_to='selection_areas/',
        blank=True,
        null=True,
        help_text='选区的图片'
    )
    
    # 创建时间
    created_at = models.DateTimeField(
        '创建时间', 
        default=timezone.now
    )
    
    # 更新时间
    updated_at = models.DateTimeField(
        '更新时间', 
        auto_now=True
    )
    
    class Meta:
        db_table = 'selection_areas'
        verbose_name = '选区定义'
        verbose_name_plural = '选区定义'
        # 添加唯一约束，防止同一班级下出现同名选区
        unique_together = ('name', 'class_info')
        # 添加默认排序规则，解决分页警告问题
        ordering = ['id']
    
    def __str__(self):
        return f'{self.class_info.kindergarten.name} - {self.class_info.name} - {self.name}'
    
    def save(self, *args, **kwargs):
        """
        重写save方法，确保在更新时不违反唯一性约束
        """
        # 检查是否是更新操作且没有改变name和class_info
        if self.pk:
            original = SelectionArea.objects.get(pk=self.pk)
            # 如果name和class_info都没有改变，则跳过唯一性检查
            if (original.name == self.name and 
                original.class_info == self.class_info):
                pass  # 允许更新
            else:
                # 如果改变了name或class_info，执行正常验证
                self.full_clean()
        else:
            # 创建新对象时执行正常验证
            self.full_clean()
        
        super().save(*args, **kwargs)

# 选区记录模型
class SelectionRecord(models.Model):
    """
    选区记录模型，记录幼儿的选区选择历史
    """
    # 关联的幼儿
    child = models.ForeignKey(
        'children.Child', 
        on_delete=models.CASCADE,
        related_name='selection_records',
        verbose_name='幼儿'
    )
    
    # 关联的选区
    selection_area = models.ForeignKey(
        'SelectionArea', 
        on_delete=models.CASCADE,
        related_name='selection_records',
        verbose_name='选区'
    )
    
    # 记录日期
    date = models.DateField(
        '记录日期',
        default=timezone.now
    )
    
    # 选择时间
    select_time = models.DateTimeField(
        '选择时间',
        default=timezone.now
    )
    
    # 操作教师
    operated_by = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='selection_records',
        verbose_name='操作教师'
    )
    
    # 状态
    is_active = models.BooleanField(
        '是否有效', 
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
        verbose_name = '选区记录'
        verbose_name_plural = '选区记录管理'
        ordering = ['-date', '-select_time']
        # 确保在同一天内，一个幼儿只能在一个选区
        unique_together = ('child', 'date')
    
    def __str__(self):
        return f'{self.child.name} - {self.selection_area.name} - {self.date}'
    
    # 获取选区所在的班级
    def get_class_info(self):
        """
        获取选区所在的班级
        """
        return self.selection_area.class_info
    
    # 获取选区所在的幼儿园
    def get_kindergarten(self):
        """
        获取选区所在的幼儿园
        """
        return self.selection_area.class_info.kindergarten