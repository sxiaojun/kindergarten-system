from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
from django.db.models import Q, Count, Prefetch
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import SelectionArea, SelectionRecord
from .serializers import (
    SelectionAreaSerializer,
    SelectionAreaBriefSerializer,
    SelectionRecordSerializer,
    SelectionRecordCreateSerializer,
    SelectionRecordUpdateSerializer,
    SelectionFilterSerializer,
    SelectionStatisticsSerializer
)
from children.models import Child
from classes.models import Class
from teachers.models import Teacher
from users.permissions import (
    IsSystemOwner,
    IsKindergartenOwnerOrSystemOwner,
    TeacherDataPermission
)
import pandas as pd
from django.http import HttpResponse
from django.utils import timezone


# 添加获取最近活动的独立视图函数
@api_view(['GET'])
@permission_classes([AllowAny])
def get_recent_activities(request):
    """
    获取最近的选区活动记录（独立视图函数）
    """
    # 获取限制参数，默认为10
    limit = int(request.query_params.get('limit', 10))
    
    # 获取最近的活动记录，按选择时间倒序排列
    recent_records = SelectionRecord.objects.select_related(
        'child', 'selection_area', 'selection_area__class_info',
        'selection_area__class_info__kindergarten', 'operated_by'
    ).order_by('-select_time')[:limit]
    
    # 序列化数据
    serializer = SelectionRecordSerializer(recent_records, many=True)
    
    return Response({
        'data': serializer.data,
        'count': len(serializer.data)
    })


# 添加获取仪表盘统计数据的独立视图函数
@api_view(['GET'])
@permission_classes([AllowAny])
def get_dashboard_stats(request):
    """
    获取仪表盘统计数据
    """
    # 根据用户角色过滤数据
    user = request.user
    kindergarten_filter = None
    class_filter = None
    
    if hasattr(user, 'role'):
        if user.role == 'principal' and hasattr(user, 'kindergarten'):
            # 园长只能看到自己幼儿园的数据
            kindergarten_filter = user.kindergarten
        elif user.role == 'teacher' and hasattr(user, 'teacher'):
            # 教师只能看到自己班级的数据
            class_filter = user.teacher.teaching_classes.all()
    
    # 获取时间范围参数
    days_param = request.query_params.get('days', '7')  # 默认7天
    try:
        days = int(days_param)
    except ValueError:
        days = 7
    
    # 限制最大天数为90天
    if days > 90:
        days = 90
    elif days < 1:
        days = 7
    
    # 获取今天的日期
    today = timezone.now().date()
    
    # 获取幼儿总数
    children_queryset = Child.objects.all()
    if kindergarten_filter:
        children_queryset = children_queryset.filter(class_info__kindergarten=kindergarten_filter)
    elif class_filter is not None:
        children_queryset = children_queryset.filter(class_info__in=class_filter)
    total_children = children_queryset.count()
    
    # 获取选区总数
    selection_areas_queryset = SelectionArea.objects.all()
    if kindergarten_filter:
        selection_areas_queryset = selection_areas_queryset.filter(
            class_info__kindergarten=kindergarten_filter
        )
    elif class_filter is not None:
        selection_areas_queryset = selection_areas_queryset.filter(
            class_info__in=class_filter
        )
    total_selection_areas = selection_areas_queryset.count()
    
    # 获取已分配选区的幼儿数（仅今天的记录）
    assigned_children_queryset = SelectionRecord.objects.filter(
        is_active=True, 
        date=today
    ).values('child').distinct()
    if kindergarten_filter:
        assigned_children_queryset = assigned_children_queryset.filter(
            child__class_info__kindergarten=kindergarten_filter
        )
    elif class_filter is not None:
        assigned_children_queryset = assigned_children_queryset.filter(
            child__class_info__in=class_filter
        )
    assigned_children = assigned_children_queryset.count()
    
    # 计算未分配选区的幼儿数
    unassigned_children = total_children - assigned_children if total_children > assigned_children else 0
    
    # 获取选区趋势数据（根据指定天数）
    selection_trend = []
    for i in range(days):
        date_point = today - timedelta(days=(days-1-i))
        
        # 构建查询
        daily_assigned_queryset = SelectionRecord.objects.filter(
            is_active=True, 
            date=date_point
        ).values('child').distinct()
        
        # 应用过滤器
        if kindergarten_filter:
            daily_assigned_queryset = daily_assigned_queryset.filter(
                child__class_info__kindergarten=kindergarten_filter
            )
        elif class_filter is not None:
            daily_assigned_queryset = daily_assigned_queryset.filter(
                child__class_info__in=class_filter
            )
            
        count = daily_assigned_queryset.count()
        selection_trend.append({
            'date': date_point.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # 获取班级总数
    classes_queryset = Class.objects.all()
    if kindergarten_filter:
        classes_queryset = classes_queryset.filter(kindergarten=kindergarten_filter)
    elif class_filter is not None:
        classes_queryset = classes_queryset.filter(id__in=class_filter)
    total_classes = classes_queryset.count()
    
    # 获取班级统计信息（班级名称和学生数量）
    class_stats = []
    classes_for_stats = Class.objects.all()
    if kindergarten_filter:
        classes_for_stats = classes_for_stats.filter(kindergarten=kindergarten_filter)
    elif class_filter is not None:
        classes_for_stats = classes_for_stats.filter(id__in=class_filter)
        
    for cls in classes_for_stats:
        # 获取班级学生数量
        student_count = Child.objects.filter(
            class_info=cls, 
            is_active=True
        ).count()
        # 始终添加班级到统计中，即使学生数为0
        class_stats.append({
            'class_id': cls.id,
            'class_name': cls.name,
            'student_count': student_count
        })
    
    # 获取教师总数
    teachers_queryset = Teacher.objects.all()
    if kindergarten_filter:
        teachers_queryset = teachers_queryset.filter(kindergarten=kindergarten_filter)
    elif class_filter is not None:
        # 教师关联到班级，需要通过班级过滤教师
        teachers_queryset = teachers_queryset.filter(
            classes__in=class_filter
        ).distinct()
    total_teachers = teachers_queryset.count()
    
    return Response({
        'total_children': total_children,
        'total_selection_areas': total_selection_areas,
        'assigned_children': assigned_children,
        'unassigned_children': unassigned_children,
        'selection_trend': selection_trend,
        'total_classes': total_classes,
        'total_teachers': total_teachers,
        'class_statistics': class_stats  # 添加班级统计信息
    })


class SelectionAreaViewSet(viewsets.ModelViewSet):
    """
    选区定义视图集
    """
    queryset = SelectionArea.objects.all()
    serializer_class = SelectionAreaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'class_info__name']
    ordering_fields = ['created_at', 'name']
    
    def get_permissions(self):
        """
        根据不同操作设置不同的权限
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # 创建、更新、删除选区仅允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action in ['list', 'retrieve']:
            # 查看选区列表和详情允许系统所有者、园长和教师
            return [IsKindergartenOwnerOrSystemOwner()]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        根据用户角色过滤查询集
        """
        queryset = super().get_queryset().select_related('class_info', 'class_info__kindergarten')
        user = self.request.user
        
        # 如果是系统所有者，返回所有选区
        if hasattr(user, 'role') and user.role == 'owner':
            return queryset
        
        # 如果是园长，返回自己幼儿园的选区
        elif hasattr(user, 'role') and user.role == 'principal' and user.kindergarten:
            return queryset.filter(class_info__kindergarten=user.kindergarten)
        
        # 如果是教师，返回自己负责班级的选区
        elif hasattr(user, 'role') and user.role == 'teacher' and user.teacher:
            return queryset.filter(
                class_info_id__in=user.teacher.teaching_classes.values_list('id', flat=True)
            )
        
        return queryset.none()
    
    def create(self, request, *args, **kwargs):
        """
        重写创建方法，处理唯一性约束错误
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            # 检查是否是唯一性约束错误
            error_str = str(e).lower()
            if 'unique constraint' in error_str or 'unique_together' in error_str or 'class_info' in error_str:
                return Response(
                    {'detail': '包含选区名称和所属班级的选区定义已经存在'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            # 其他验证错误
            return Response(
                {'detail': '包含选区名称和所属班级的选区定义已经存在', 'errors': e.message_dict},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # 其他异常
            return Response(
                {'detail': '创建失败: ' + str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        重写更新方法，处理唯一性约束错误
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except ValidationError as e:
            # 检查是否是唯一性约束错误
            error_str = str(e).lower()
            if 'unique constraint' in error_str or 'unique_together' in error_str:
                return Response(
                    {'detail': '包含选区名称和所属班级的选区定义已经存在'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            # 其他验证错误
            return Response(
                {'detail': '包含选区名称和所属班级的选区定义已经存在', 'errors': e.message_dict},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # 其他异常
            return Response(
                {'detail': '更新失败: ' + str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """
        重写列表方法，支持按班级筛选
        """
        queryset = self.get_queryset()
        
        # 支持按名称筛选
        name = request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        # 按班级筛选
        class_id = request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(class_info_id=class_id)
        
        # 应用分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'items': serializer.data,
                'total': self.paginator.page.paginator.count
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'items': serializer.data,
            'total': len(queryset)
        })
    
    @action(detail=True, methods=['patch'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def toggle_status(self, request, pk=None):
        """
        切换选区状态
        """
        selection_area = self.get_object()
        selection_area.is_active = not selection_area.is_active
        selection_area.save()
        
        return Response({
            'id': selection_area.id,
            'is_active': selection_area.is_active,
            'message': '状态更新成功'
        })

class SelectionRecordViewSet(viewsets.ModelViewSet):
    """
    选区记录视图集
    """
    queryset = SelectionRecord.objects.all()
    serializer_class = SelectionRecordSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['child__name', 'selection_area__name']
    ordering_fields = ['date', 'select_time', 'child__name']
    
    def get_permissions(self):
        """
        根据不同操作设置不同的权限
        """
        if self.action == 'create':
            # 创建选区记录允许系统所有者、园长和教师
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # 更新、删除选区记录仅允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action in ['list', 'retrieve']:
            # 查看选区记录允许系统所有者、园长和教师
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action in ['batch_create', 'end_selection']:
            # 批量创建和结束选区选择仅允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action in ['history', 'active', 'export']:
            # 历史记录、当前有效记录和导出功能允许系统所有者、园长和教师
            return [IsKindergartenOwnerOrSystemOwner()]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        根据用户角色过滤查询集
        """
        queryset = super().get_queryset().select_related(
            'child', 'selection_area', 'selection_area__class_info',
            'selection_area__class_info__kindergarten', 'operated_by'
        )
        user = self.request.user
        
        # 如果是系统所有者，返回所有记录
        if hasattr(user, 'role') and user.role == 'owner':
            return queryset
        
        # 如果是园长，返回自己幼儿园的记录
        elif hasattr(user, 'role') and user.role == 'principal' and user.kindergarten:
            return queryset.filter(selection_area__class_info__kindergarten=user.kindergarten)
        
        # 如果是教师，返回自己负责班级的记录
        elif hasattr(user, 'role') and user.role == 'teacher' and user.teacher:
            return queryset.filter(
                selection_area__class_info_id__in=user.teacher.classes.values_list('id', flat=True)
            )
        
        return queryset.none()
    
    def get_serializer_class(self):
        """
        根据操作选择不同的序列化器
        """
        if self.action == 'create':
            return SelectionRecordCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SelectionRecordUpdateSerializer
        return super().get_serializer_class()
    
    def create(self, request, *args, **kwargs):
        """
        创建选区记录
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # 返回完整序列化数据
        response_serializer = SelectionRecordSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        """
        重写列表方法，支持多种筛选条件
        """
        queryset = self.get_queryset()
        
        # 应用筛选条件
        class_id = request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(selection_area__class_info_id=class_id)
        
        kindergarten_id = request.query_params.get('kindergarten_id')
        if kindergarten_id:
            queryset = queryset.filter(selection_area__class_info__kindergarten_id=kindergarten_id)
        
        child_name = request.query_params.get('child_name')
        if child_name:
            queryset = queryset.filter(child__name__icontains=child_name)
        
        selection_area_id = request.query_params.get('selection_area_id')
        if selection_area_id:
            queryset = queryset.filter(selection_area_id=selection_area_id)
        
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        
        operated_by = request.query_params.get('operated_by')
        if operated_by:
            queryset = queryset.filter(operated_by_id=operated_by)
        
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # 应用分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def batch_create(self, request):
        """
        批量创建选区记录
        """
        records_data = request.data.get('records', [])
        created_records = []
        
        for record_data in records_data:
            serializer = SelectionRecordCreateSerializer(data=record_data)
            if serializer.is_valid():
                instance = serializer.save()
                created_records.append(instance)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 返回创建的记录
        response_serializer = SelectionRecordSerializer(created_records, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def end_selection(self, request, pk=None):
        """
        结束选区选择（标记为无效）
        """
        selection_record = self.get_object()
        selection_record.is_active = False
        selection_record.save()
        
        # 返回更新后的数据
        serializer = self.get_serializer(selection_record)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def history(self, request, pk=None):
        """
        获取指定幼儿的选区历史记录
        """
        child_id = pk
        history_records = SelectionRecord.objects.filter(child_id=child_id).select_related(
            'selection_area', 'selection_area__class_info', 'operated_by'
        ).order_by('-date', '-select_time')
        
        serializer = self.get_serializer(history_records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def active(self, request):
        """
        获取当前有效的选区记录
        """
        today = date.today()
        active_records = SelectionRecord.objects.filter(
            date=today, is_active=True
        ).select_related(
            'child', 'selection_area', 'selection_area__class_info',
            'selection_area__class_info__kindergarten', 'operated_by'
        ).order_by('selection_area', 'select_time')
        
        serializer = self.get_serializer(active_records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def export(self, request):
        """
        导出选区记录为Excel文件
        """
        # 获取查询参数
        queryset = self.get_queryset()
        
        # 应用筛选条件
        class_id = request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(selection_area__class_info_id=class_id)
        
        child_name = request.query_params.get('child_name')
        if child_name:
            queryset = queryset.filter(child__name__icontains=child_name)
        
        selection_area_id = request.query_params.get('selection_area_id')
        if selection_area_id:
            queryset = queryset.filter(selection_area_id=selection_area_id)
        
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # 应用排序
        ordering = request.query_params.get('ordering', '-select_time')
        queryset = queryset.order_by(ordering)
        
        # 序列化数据
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        
        # 创建DataFrame
        df_data = []
        for item in data:
            df_data.append({
                '幼儿姓名': item.get('child_name', ''),
                '选区名称': item.get('selection_area_name', ''),
                '所属班级': item.get('class_name', ''),
                '选择时间': item.get('select_time', ''),
                '备注': item.get('notes', ''),
            })
        
        df = pd.DataFrame(df_data)
        
        # 创建响应
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="selection_records_{date.today().strftime("%Y%m%d")}.xlsx"'
        
        # 写入Excel
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='选区记录')
            
        return response
