from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q, Count
from .models import Kindergarten
from .serializers import (
    KindergartenSerializer,
    KindergartenBriefSerializer,
    KindergartenImportSerializer
)
from users.permissions import (
    IsSystemOwner,
    IsKindergartenOwnerOrSystemOwner,
    KindergartenDataPermission
)
import pandas as pd
from datetime import datetime
import os

# 幼儿园视图集
class KindergartenViewSet(viewsets.ModelViewSet):
    queryset = Kindergarten.objects.all()
    serializer_class = KindergartenSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address', 'principal_name', 'phone', 'region']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at']
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    
    def get_permissions(self):
        """
        根据不同操作设置不同的权限
        """
        if self.action == 'create':
            # 创建幼儿园仅允许系统所有者
            return [IsSystemOwner()]
        elif self.action == 'list':
            # 查看幼儿园列表允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'retrieve':
            # 查看幼儿园详情允许系统所有者和该幼儿园的园长
            return [KindergartenDataPermission()]
        elif self.action == 'update' or self.action == 'partial_update':
            # 更新幼儿园信息仅允许系统所有者和该幼儿园的园长
            return [KindergartenDataPermission()]
        elif self.action == 'destroy':
            # 删除幼儿园仅允许系统所有者
            return [IsSystemOwner()]
        elif self.action in ['import_data', 'export_template']:
            # 导入导出功能允许系统所有者
            return [IsSystemOwner()]
        elif self.action == 'active':
            # 获取激活状态的幼儿园允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'stats':
            # 获取统计信息允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        根据用户角色过滤查询集
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # 如果是系统所有者，返回所有幼儿园
        if hasattr(user, 'role') and user.role == 'owner':
            queryset = queryset
        # 如果是园长，只返回自己管理的幼儿园
        elif hasattr(user, 'role') and user.role == 'principal' and user.kindergarten:
            queryset = queryset.filter(id=user.kindergarten.id)
        else:
            queryset = queryset.none()
        
        # 获取查询参数
        name = self.request.query_params.get('name', None)
        region = self.request.query_params.get('region', None)
        
        # 根据参数进行过滤
        if name:
            queryset = queryset.filter(
                Q(name__icontains=name) | 
                Q(address__icontains=name) | 
                Q(principal_name__icontains=name) | 
                Q(phone__icontains=name) |
                Q(region__icontains=name)
            )
        elif region:  # 只有当name为空时才单独按region搜索
            queryset = queryset.filter(region__icontains=region)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        重写列表方法以适应分页需求
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        创建幼儿园
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kindergarten = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        更新幼儿园信息
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
        获取所有幼儿园
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSystemOwner])
    def activate(self, request, pk=None):
        """
        激活幼儿园
        """
        kindergarten = self.get_object()
        kindergarten.status = 'active'
        kindergarten.save()
        return Response({'status': 'kindergarten activated'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsSystemOwner])
    def deactivate(self, request, pk=None):
        """
        停用幼儿园
        """
        kindergarten = self.get_object()
        kindergarten.status = 'inactive'
        kindergarten.save()
        return Response({'status': 'kindergarten deactivated'})
    
    @action(detail=False, methods=['post'], permission_classes=[IsSystemOwner], parser_classes=[MultiPartParser, FormParser])
    def import_data(self, request):
        """
        批量导入幼儿园数据
        """
        serializer = KindergartenImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file = request.FILES['file']
        try:
            # 读取Excel文件
            df = pd.read_excel(file)
            
            # 检查必要的列
            required_columns = ['名称', '类型', '地址', '联系人', '联系电话', '园长', '最大学生数', '最大教师数']
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
                    # 检查幼儿园是否已存在
                    if Kindergarten.objects.filter(name=row['名称']).exists():
                        errors.append(f"第{index+2}行: 幼儿园 '{row['名称']}' 已存在")
                        continue
                    
                    # 转换类型
                    kindergarten_type_map = {
                        '公立': 'public',
                        '私立': 'private',
                        '普惠': 'inclusive'
                    }
                    kindergarten_type = kindergarten_type_map.get(row['类型'], 'private')
                    
                    # 创建幼儿园
                    kindergarten_data = {
                        'name': row['名称'],
                        'kindergarten_type': kindergarten_type,
                        'address': row['地址'],
                        'contact_person': row['联系人'],
                        'contact_phone': row['联系电话'],
                        'principal': row['园长'],
                        'max_students': int(row['最大学生数']),
                        'max_teachers': int(row['最大教师数'])
                    }
                    
                    # 处理可选字段
                    if '成立日期' in row and pd.notna(row['成立日期']):
                        kindergarten_data['established_date'] = row['成立日期']
                    if '描述' in row and pd.notna(row['描述']):
                        kindergarten_data['description'] = row['描述']
                    
                    Kindergarten.objects.create(**kindergarten_data)
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
    
    @action(detail=False, methods=['get'], permission_classes=[IsSystemOwner])
    def export_template(self, request):
        """
        导出幼儿园数据导入模板
        """
        # 创建模板数据
        template_data = {
            '名称': ['示例幼儿园1', '示例幼儿园2'],
            '类型': ['公立', '私立'],  # 可选值：公立、私立、普惠
            '地址': ['北京市朝阳区XX路1号', '上海市浦东新区YY路2号'],
            '联系人': ['张三', '李四'],
            '联系电话': ['13800138001', '13900139002'],
            '园长': ['王五', '赵六'],
            '最大学生数': [300, 200],
            '最大教师数': [30, 20],
            '成立日期': ['2020-01-01', '2021-02-02'],  # 可选
            '描述': ['这是一所公立幼儿园', '这是一所私立幼儿园']  # 可选
        }
        
        df = pd.DataFrame(template_data)
        
        # 创建响应
        from django.http import HttpResponse
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=kindergarten_template_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        # 保存到响应
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='幼儿园信息')
        
        return response
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def stats(self, request):
        """
        获取幼儿园统计信息
        """
        queryset = self.get_queryset()
        
        # 统计总数
        total_count = queryset.count()
        
        # 按类型统计
        type_stats = queryset.values('kindergarten_type').annotate(count=Count('id'))
        
        # 计算总学生数和教师数
        total_students = sum(k.get_student_count() for k in queryset)
        total_teachers = sum(k.get_teacher_count() for k in queryset)
        total_classes = sum(k.get_class_count() for k in queryset)
        
        stats = {
            'total_count': total_count,
            'type_stats': type_stats,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_classes': total_classes
        }
        
        return Response(stats)