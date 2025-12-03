from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Class
from .serializers import (
    ClassSerializer,
    ClassBriefSerializer,
    ClassImportSerializer
)
from users.permissions import (
    IsSystemOwner,
    IsKindergartenOwnerOrSystemOwner,
    ClassDataPermission,
    TeacherDataPermission
)
import pandas as pd
from datetime import datetime

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'class_type', 'kindergarten__name']
    ordering_fields = ['id', 'name', 'kindergarten', 'created_at', 'updated_at']
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        """
        根据用户角色过滤查询集
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # 如果是系统所有者，返回所有班级
        if hasattr(user, 'role') and user.role == 'owner':
            pass  # 不进行额外过滤
        # 如果是园长，返回自己幼儿园的班级
        elif hasattr(user, 'role') and user.role == 'principal' and user.kindergarten:
            queryset = queryset.filter(kindergarten=user.kindergarten)
        # 如果是教师，返回自己负责的班级
        elif hasattr(user, 'role') and user.role == 'teacher' and user.teacher:
            queryset = queryset.filter(id__in=user.teacher.classes.values_list('id', flat=True))
        else:
            queryset = queryset.none()
        
        # 获取查询参数
        name = self.request.query_params.get('name', None)
        class_type = self.request.query_params.get('class_type', None)
        
        # 根据参数进行过滤
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        if class_type:
            queryset = queryset.filter(class_type=class_type)
            
        return queryset

    def get_permissions(self):
        """
        根据不同操作设置不同的权限
        """
        if self.action == 'create':
            # 创建班级仅允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'list':
            # 查看班级列表允许系统所有者、园长和教师
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'retrieve':
            # 查看班级详情允许系统所有者、园长和该班级的教师
            return [ClassDataPermission()]
        elif self.action == 'update' or self.action == 'partial_update':
            # 更新班级信息仅允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'destroy':
            # 删除班级仅允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action in ['import_data', 'export_template', 'update_student_counts']:
            # 导入导出和更新学生数量功能允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action in ['active', 'options', 'stats']:
            # 获取激活状态的班级、选项列表和统计信息允许系统所有者、园长和教师
            return [IsKindergartenOwnerOrSystemOwner()]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        """
        创建班级
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        class_obj = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        更新班级信息
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def active(self, request):
        """
        获取所有激活状态的班级
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsKindergartenOwnerOrSystemOwner], parser_classes=[MultiPartParser, FormParser])
    def import_data(self, request):
        """
        批量导入班级数据
        """
        serializer = ClassImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file = request.FILES['file']
        user = request.user
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file)
            
            # 检查必要的列
            required_columns = ['班级名称(*)', '班级类型(*)']
            if user.role == 'system_owner':
                required_columns.append('幼儿园名称(*)')
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response(
                    {'error': f'缺少必要的列: {missing_columns}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            created_count = 0
            errors = []
            
            # 处理每一行数据
            for index, row in df.iterrows():
                try:
                    # 确定幼儿园ID
                    if user.role == 'system_owner':
                        if '幼儿园名称(*)' not in row or pd.isna(row['幼儿园名称(*)']):
                            errors.append(f"第{index+2}行: 幼儿园名称不能为空")
                            continue
                        from kindergartens.models import Kindergarten
                        try:
                            kindergarten = Kindergarten.objects.get(name=row['幼儿园名称(*)'])
                            kindergarten_id = kindergarten.id
                        except Kindergarten.DoesNotExist:
                            errors.append(f"第{index+2}行: 幼儿园 '{row['幼儿园名称(*)']}' 不存在")
                            continue
                    else:
                        # 对于教师用户，从关联的教师记录中获取幼儿园信息
                        if user.role == 'teacher' and hasattr(user, 'teacher') and user.teacher:
                            kindergarten_id = user.teacher.kindergarten.id
                        else:
                            kindergarten_id = user.kindergarten.id
                    
                    # 检查班级是否已存在
                    if Class.objects.filter(name=row['班级名称(*)'], kindergarten_id=kindergarten_id).exists():
                        errors.append(f"第{index+2}行: 班级 '{row['班级名称(*)']}' 已存在")
                        continue
                    
                    # 转换类型
                    class_type_map = {
                        '托儿所': 'nursery',
                        '小班': 'small',
                        '中班': 'middle',
                        '大班': 'large',
                        '学前班': 'pre_school'
                    }
                    class_type = class_type_map.get(row['班级类型(*)'], 'small')
                    
                    # 创建班级
                    class_data = {
                        'name': row['班级名称(*)'],
                        'class_type': class_type,
                        'kindergarten_id': kindergarten_id
                    }
                    
                    # 处理可选字段
                    if '班级描述' in row and pd.notna(row['班级描述']):
                        class_data['description'] = row['班级描述']
                    
                    Class.objects.create(**class_data)
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"第{index+2}行: {str(e)}")
            
            result = {
                'created_count': created_count,
                'total_rows': len(df),
                'errors': errors
            }
            
            if errors:
                return Response(result, status=status.HTTP_207_MULTI_STATUS)
            else:
                return Response(result, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': f'导入失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def export_template(self, request):
        """
        导出班级数据导入模板
        """
        user = request.user
        
        # 创建模板数据
        template_data = {
            '班级名称(*)': ['大一班', '小一班'],
            '班级类型(*)': ['大班', '小班'],  # 可选值：托儿所、小班、中班、大班、学前班
            '班级描述': ['大班教室', '小班教室']  # 可选
        }
        
        # 只有系统所有者需要选择幼儿园
        if user.role == 'system_owner':
            template_data['幼儿园名称(*)'] = ['幼儿园A', '幼儿园B']  # 示例名称
        
        df = pd.DataFrame(template_data)
        
        # 创建响应
        from django.http import HttpResponse
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=class_template_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        # 保存到响应
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='班级信息')
        
        return response
    
    @action(detail=False, methods=['post'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def update_student_counts(self, request):
        """
        批量更新所有班级的学生数量
        """
        queryset = self.get_queryset()
        updated_count = 0
        
        for class_obj in queryset:
            class_obj.update_student_count()
            updated_count += 1
        
        return Response({
            'updated_count': updated_count,
            'message': f'成功更新了{updated_count}个班级的学生数量'
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def options(self, request):
        """
        获取班级选项列表（用于下拉选择）
        """
        queryset = self.get_queryset()
        serializer = ClassBriefSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def stats(self, request):
        """
        获取班级统计信息
        """
        queryset = self.get_queryset()
        
        # 统计总数
        total_count = queryset.count()
        
        # 按类型统计
        type_stats = queryset.values('class_type').annotate(count=Count('id'))
        
        stats = {
            'total_count': total_count,
            'type_stats': type_stats
        }
        
        return Response(stats)