from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q, Count
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid
from .models import Child
from .serializers import (
    ChildSerializer,
    ChildBriefSerializer,
    ChildImportSerializer,
    ChildFilterSerializer
)
from users.permissions import (
    IsSystemOwner,
    IsKindergartenOwnerOrSystemOwner,
    ChildDataPermission,
    TeacherDataPermission
)
import pandas as pd
from datetime import datetime, timezone
import io

class ChildViewSet(viewsets.ModelViewSet):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'parent_name', 'parent_phone', 'student_id']
    ordering_fields = ['id', 'name', 'created_at', 'updated_at', 'admission_date']
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_permissions(self):
        """
        根据不同操作设置不同的权限
        """
        if self.action == 'create':
            # 创建幼儿仅允许系统所有者、园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'list':
            # 查看幼儿列表允许系统所有者、园长和教师
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'retrieve':
            # 查看幼儿详情允许系统所有者、园长和该幼儿班级的教师
            return [ChildDataPermission()]
        elif self.action == 'update' or self.action == 'partial_update':
            # 更新幼儿信息仅允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'destroy':
            # 删除幼儿仅允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action in ['import_data', 'export_template', 'export_data', 'statistics', 'attendance_statistics']:
            # 导入导出和统计功能允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action in ['toggle_status']:
            # 切换状态功能允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action in ['active']:
            # 获取激活状态的幼儿允许系统所有者、园长和教师
            return [IsKindergartenOwnerOrSystemOwner()]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        根据用户角色过滤查询集
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # 如果是系统所有者，返回所有幼儿
        if hasattr(user, 'role') and user.role == 'owner':
            return queryset
        
        # 如果是园长，返回自己幼儿园的幼儿
        elif hasattr(user, 'role') and user.role == 'principal' and user.kindergarten:
            return queryset.filter(class_info__kindergarten=user.kindergarten)
        
        # 如果是教师，返回自己负责班级的幼儿
        elif hasattr(user, 'role') and user.role == 'teacher' and user.teacher:
            return queryset.filter(class_info__in=user.teacher.classes.all())
        
        return queryset.none()
    
    def list(self, request, *args, **kwargs):
        """
        重写列表方法，支持分页和筛选
        """
        # 解析筛选参数
        filter_serializer = ChildFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filter_params = filter_serializer.validated_data
        
        # 应用筛选条件
        queryset = self.get_queryset()
        
        # 只有当参数有值时才应用过滤条件（支持单字段和多字段联合查询）
        if filter_params.get('name') and filter_params['name'].strip():
            queryset = queryset.filter(name__icontains=filter_params['name'].strip())
        
        if filter_params.get('class_id'):
            queryset = queryset.filter(class_info_id=filter_params['class_id'])
        
        if filter_params.get('parent_name') and filter_params['parent_name'].strip():
            queryset = queryset.filter(parent_name__icontains=filter_params['parent_name'].strip())
        
        if filter_params.get('parent_phone') and filter_params['parent_phone'].strip():
            queryset = queryset.filter(parent_phone__icontains=filter_params['parent_phone'].strip())
        
        if filter_params.get('status'):
            is_active = filter_params['status'] == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        if filter_params.get('kindergarten_id'):
            queryset = queryset.filter(class_info__kindergarten_id=filter_params['kindergarten_id'])
        
        if filter_params.get('date_start'):
            queryset = queryset.filter(admission_date__gte=filter_params['date_start'])
        
        if filter_params.get('date_end'):
            queryset = queryset.filter(admission_date__lte=filter_params['date_end'])
        
        # 应用分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        获取幼儿详情
        """
        instance = self.get_object()
        # 构建完整的响应数据
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        创建幼儿记录
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        child = serializer.save()
        
        # 自动生成学号（如果没有提供）
        if not child.student_id:
            # 生成学号格式：幼儿园ID-班级ID-4位序号
            kind_id = child.class_info.kindergarten.id if child.class_info and child.class_info.kindergarten else '00'
            class_id = child.class_info.id if child.class_info else '00'
            # 获取该班级的最大序号
            max_seq = Child.objects.filter(class_info_id=child.class_info_id).aggregate(Count('id'))['id__count']
            child.student_id = f"{kind_id}-{class_id}-{max_seq:04d}"
            child.save()
        
        # 重新序列化以包含生成的学号
        serializer = self.get_serializer(child)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def active(self, request):
        """
        获取所有在读状态的幼儿
        """
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'items': serializer.data,
            'total': len(queryset)
        })
    
    @action(detail=True, methods=['patch'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def toggle_status(self, request, pk=None):
        """
        切换幼儿状态
        """
        child = self.get_object()
        status_data = request.data.get('status')
        
        if status_data:
            child.is_active = (status_data == 'active')
        else:
            # 如果没有指定状态，直接切换
            child.is_active = not child.is_active
        
        child.save()
        return Response({
            'id': child.id,
            'status': 'active' if child.is_active else 'inactive',
            'message': '状态更新成功'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsKindergartenOwnerOrSystemOwner], parser_classes=[MultiPartParser, FormParser])
    def upload_avatar(self, request, pk=None):
        """
        上传幼儿头像
        """
        child = self.get_object()
        
        # 检查是否有上传文件
        if 'avatar' not in request.FILES:
            return Response({'error': '未找到上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        avatar_file = request.FILES['avatar']
        
        # 删除旧头像文件（如果存在）
        if child.avatar:
            if default_storage.exists(child.avatar.name):
                default_storage.delete(child.avatar.name)
        
        # 生成唯一的文件名
        ext = os.path.splitext(avatar_file.name)[1]
        filename = f"child_avatars/{uuid.uuid4().hex}{ext}"
        
        # 保存文件
        path = default_storage.save(filename, ContentFile(avatar_file.read()))
        
        # 更新幼儿头像字段
        child.avatar = path
        child.save()
        
        return Response({
            'avatar': child.avatar.url,
            'message': '头像上传成功'
        })

    @action(detail=True, methods=['delete'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def delete_avatar(self, request, pk=None):
        """
        删除幼儿头像
        """
        child = self.get_object()
        
        # 检查是否有头像文件
        if not child.avatar:
            return Response({'error': '该幼儿没有头像文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 删除头像文件（如果存在）
        if default_storage.exists(child.avatar.name):
            default_storage.delete(child.avatar.name)
        
        # 清空幼儿头像字段
        child.avatar = None
        child.save()
        
        return Response({
            'message': '头像删除成功'
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsKindergartenOwnerOrSystemOwner], parser_classes=[MultiPartParser, FormParser])
    def import_data(self, request):
        """
        批量导入幼儿数据
        """
        serializer = ChildImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file = request.FILES['file']
        user = request.user
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file)
            
            # 检查必要的列
            required_columns = ['幼儿姓名(*)', '性别(*)', '出生日期(*)', '班级名称(*)', '家长姓名', '家长手机号']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response(
                    {'error': f'缺少必要的列: {missing_columns}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            created_count = 0
            updated_count = 0
            errors = []
            
            # 处理每一行数据
            for index, row in df.iterrows():
                try:
                    # 转换性别
                    gender_map = {'男': 'male', '女': 'female'}
                    gender = gender_map.get(row['性别(*)'], 'male')
                    
                    # 根据班级名称查找班级ID
                    class_info = None
                    if '班级名称(*)' in row and pd.notna(row['班级名称(*)']):
                        from classes.models import Class
                        if user.role == 'owner':
                            # 系统管理员需要指定幼儿园
                            if '幼儿园名称' in df.columns and pd.notna(row.get('幼儿园名称')):
                                from kindergartens.models import Kindergarten
                                try:
                                    kindergarten = Kindergarten.objects.get(name=row['幼儿园名称'])
                                    class_info = Class.objects.get(name=row['班级名称(*)'], kindergarten=kindergarten)
                                except Kindergarten.DoesNotExist:
                                    errors.append(f"第{index+2}行: 幼儿园 '{row['幼儿园名称']}' 不存在")
                                    continue
                                except Class.DoesNotExist:
                                    errors.append(f"第{index+2}行: 班级 '{row['班级名称(*)']}' 在指定幼儿园中不存在")
                                    continue
                            else:
                                errors.append(f"第{index+2}行: 系统管理员需要提供幼儿园名称")
                                continue
                        else:
                            # 其他用户根据所属幼儿园查找班级
                            try:
                                # 对于教师用户，从关联的教师记录中获取幼儿园信息
                                if user.role == 'teacher' and hasattr(user, 'teacher') and user.teacher:
                                    kindergarten = user.teacher.kindergarten
                                else:
                                    kindergarten = user.kindergarten
                                class_info = Class.objects.get(name=row['班级名称(*)'], kindergarten=kindergarten)
                            except Class.DoesNotExist:
                                errors.append(f"第{index+2}行: 班级 '{row['班级名称(*)']}' 在您的幼儿园中不存在")
                                continue
                    
                    # 准备数据
                    child_data = {
                        'name': str(row['幼儿姓名(*)']).strip(),
                        'gender': gender,
                        'birth_date': pd.to_datetime(row['出生日期(*)']).date(),
                        'class_id': class_info.id if class_info else None,
                        'parent_name': str(row['家长姓名']).strip() if pd.notna(row['家长姓名']) else '',
                        'parent_phone': str(row['家长手机号']).strip() if pd.notna(row['家长手机号']) else ''
                    }
                    
                    # 处理可选字段
                    if '学号' in row and pd.notna(row['学号']):
                        child_data['student_id'] = str(row['学号']).strip()
                    
                    if '入园日期' in row and pd.notna(row['入园日期']):
                        child_data['admission_date'] = pd.to_datetime(row['入园日期']).date()
                    else:
                        child_data['admission_date'] = datetime.now().date()
                    
                    if '家长邮箱' in row and pd.notna(row['家长邮箱']):
                        child_data['parent_email'] = str(row['家长邮箱']).strip()
                    
                    if '家庭地址' in row and pd.notna(row['家庭地址']):
                        child_data['home_address'] = str(row['家庭地址']).strip()
                    
                    if '健康备注' in row and pd.notna(row['健康备注']):
                        child_data['health_notes'] = str(row['健康备注']).strip()
                    
                    if '备注' in row and pd.notna(row['备注']):
                        child_data['notes'] = str(row['备注']).strip()
                    
                    # 处理头像URL
                    avatar_file_path = None
                    if '头像URL' in row and pd.notna(row['头像URL']):
                        avatar_url = str(row['头像URL']).strip()
                        # 如果是本地文件路径，记录文件路径以便后续处理
                        if avatar_url.startswith('file:///'):
                            # 从本地文件路径导入头像
                            try:
                                import urllib.request
                                import os
                                
                                # 移除file:///前缀并解码URL
                                file_path = urllib.parse.unquote(avatar_url[8:])  # 移除'file:///'
                                if os.path.exists(file_path):
                                    avatar_file_path = file_path
                                else:
                                    errors.append(f"第{index+2}行: 头像文件不存在 {file_path}")
                            except Exception as e:
                                errors.append(f"第{index+2}行: 头像文件处理失败 {str(e)}")
                        else:
                            # 处理网络URL或其他形式的URL
                            child_data['avatar'] = avatar_url
                    
                    # 检查是否已存在
                    existing_child = None
                    if '学号' in child_data and child_data['student_id']:
                        existing_child = Child.objects.filter(student_id=child_data['student_id']).first()
                    
                    if existing_child:
                        # 更新现有记录
                        serializer = ChildSerializer(existing_child, data=child_data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        child_instance = serializer.save()
                        
                        # 如果有本地头像文件，需要特殊处理
                        if avatar_file_path:
                            try:
                                from django.core.files import File
                                import os
                                
                                with open(avatar_file_path, 'rb') as f:
                                    # 生成文件名
                                    filename = os.path.basename(avatar_file_path)
                                    # 保存文件到Django存储系统
                                    child_instance.avatar.save(filename, File(f), save=True)
                            except Exception as e:
                                errors.append(f"第{index+2}行: 头像文件保存失败 {str(e)}")
                        
                        updated_count += 1
                    else:
                        # 创建新记录
                        serializer = ChildSerializer(data=child_data)
                        serializer.is_valid(raise_exception=True)
                        child_instance = serializer.save()
                        
                        # 如果有本地头像文件，需要特殊处理
                        if avatar_file_path:
                            try:
                                from django.core.files import File
                                import os
                                
                                with open(avatar_file_path, 'rb') as f:
                                    # 生成文件名
                                    filename = os.path.basename(avatar_file_path)
                                    # 保存文件到Django存储系统
                                    child_instance.avatar.save(filename, File(f), save=True)
                            except Exception as e:
                                errors.append(f"第{index+2}行: 头像文件保存失败 {str(e)}")
                        
                        created_count += 1
                        
                except Exception as e:
                    errors.append(f"第{index+2}行: {str(e)}")
            
            result = {
                'created_count': created_count,
                'updated_count': updated_count,
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
        导出幼儿数据导入模板
        """
        # 创建模板数据
        template_data = {
            '幼儿姓名(*)': ['张三', '李四'],
            '性别(*)': ['男', '女'],
            '出生日期(*)': ['2020-01-01', '2020-02-02'],
            '班级名称(*)': ['大一班', '小一班'],
            '学号': ['', ''],
            '入园日期': ['2023-09-01', '2023-09-01'],
            '家长姓名': ['张三爸爸', '李四妈妈'],
            '家长手机号': ['13800138001', '13900139002'],
            '家长邮箱': ['', ''],
            '家庭地址': ['北京市朝阳区XX小区', '上海市浦东新区XX路'],
            '健康备注': ['无', '对海鲜过敏'],
            '头像URL': ['', ''],  # 头像URL列
            '备注': ['', '']
        }
        
        df = pd.DataFrame(template_data)
        
        # 创建响应
        from django.http import HttpResponse
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=child_template_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        # 保存到响应
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='幼儿信息')
        
        return response
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def export_data(self, request):
        """
        导出幼儿数据
        """
        # 应用筛选条件
        filter_serializer = ChildFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filter_params = filter_serializer.validated_data
        
        queryset = self.get_queryset()
        
        # 应用筛选条件
        if filter_params.get('name'):
            queryset = queryset.filter(name__icontains=filter_params['name'])
        if filter_params.get('class_id'):
            queryset = queryset.filter(class_info_id=filter_params['class_id'])
        # 其他筛选条件...
        
        # 获取数据
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        
        # 转换为导出格式
        export_data = []
        for item in data:
            export_data.append({
                '幼儿ID': item['id'],
                '幼儿姓名': item['name'],
                '性别': '男' if item['gender'] == 'male' else '女',
                '出生日期': item['birth_date'],
                '年龄': item['age'],
                '班级': item['class_info']['name'] if item['class_info'] else '',
                '学号': item['student_id'] or '',
                '入园日期': item['admission_date'],
                '家长姓名': item['parent_name'],
                '家长手机号': item['parent_phone'],
                '家庭地址': item['home_address'] or '',
                '状态': '在读' if item['status'] == 'active' else '已毕业',
                '创建时间': item['created_at']
            })
        
        df = pd.DataFrame(export_data)
        
        # 创建响应
        from django.http import HttpResponse
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=children_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        # 保存到响应
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='幼儿信息')
        
        return response
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def statistics(self, request):
        """
        获取幼儿统计信息
        """
        queryset = self.get_queryset()
        
        # 总统计
        total_count = queryset.count()
        active_count = queryset.filter(is_active=True).count()
        inactive_count = queryset.filter(is_active=False).count()
        
        # 按性别统计
        gender_stats = queryset.values('gender').annotate(count=Count('id'))
        gender_data = {item['gender']: item['count'] for item in gender_stats}
        
        # 按班级统计
        class_stats = queryset.values('class_info__name', 'class_info__id').annotate(count=Count('id'))
        
        # 按年龄段统计
        age_stats = []
        age_ranges = [(0, 3), (3, 4), (4, 5), (5, 6), (6, 10)]
        for min_age, max_age in age_ranges:
            count = 0
            for child in queryset:
                age = child.get_age()
                if age is not None and min_age <= age < max_age:
                    count += 1
            age_stats.append({
                'range': f'{min_age}-{max_age}岁',
                'count': count
            })
        
        # 入园统计（按月）
        admission_stats = []
        # 这里简化处理，实际可以根据需求做更复杂的统计
        
        return Response({
            'total_count': total_count,
            'active_count': active_count,
            'inactive_count': inactive_count,
            'gender_stats': gender_data,
            'class_stats': class_stats,
            'age_stats': age_stats,
            'admission_stats': admission_stats
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def attendance_statistics(self, request):
        """
        获取幼儿出勤统计
        """
        # 这里简化处理，实际应该与出勤系统集成
        # 暂时返回模拟数据
        return Response({
            'message': '出勤统计功能待实现',
            'status': 'pending'
        })

