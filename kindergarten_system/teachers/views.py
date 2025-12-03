from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Teacher
from .serializers import (
    TeacherSerializer,
    TeacherBriefSerializer,
    TeacherImportSerializer,
    TeacherStatsSerializer
)
from users.permissions import (
    IsSystemOwner,
    IsKindergartenOwnerOrSystemOwner,
    TeacherDataPermission
)
import pandas as pd
import io

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone', 'email', 'position', 'kindergarten__name']
    ordering_fields = ['id', 'name', 'position', 'hire_date', 'created_at', 'updated_at']
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_permissions(self):
        """
        根据不同操作设置不同的权限
        """
        if self.action == 'create':
            # 创建教师仅允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'list':
            # 查看教师列表允许系统所有者、园长和教师
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'retrieve':
            # 查看教师详情允许系统所有者、园长和教师自己
            return [TeacherDataPermission()]
        elif self.action == 'update' or self.action == 'partial_update':
            # 更新教师信息仅允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'destroy':
            # 删除教师仅允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action in ['import_data', 'export_template', 'activate', 'deactivate']:
            # 导入导出和激活停用功能允许系统所有者和园长
            return [IsKindergartenOwnerOrSystemOwner()]
        elif self.action == 'class_responsibilities':
            # 教师负责的班级详情允许教师自己查看
            return [IsKindergartenOwnerOrSystemOwner()]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        根据用户角色过滤查询集，并支持额外的查询参数过滤
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # 如果是系统所有者，返回所有教师
        if hasattr(user, 'role') and user.role == 'owner':
            queryset = queryset
        # 如果是园长，返回自己幼儿园的教师
        elif hasattr(user, 'role') and user.role == 'principal' and user.kindergarten:
            queryset = queryset.filter(kindergarten=user.kindergarten)
        # 如果是教师，只能查看自己的信息
        elif hasattr(user, 'role') and user.role == 'teacher' and user.teacher:
            queryset = queryset.filter(id=user.teacher.id)
        else:
            queryset = queryset.none()
        
        # 获取查询参数
        name = self.request.query_params.get('name', None)
        employee_id = self.request.query_params.get('employee_id', None)
        phone = self.request.query_params.get('phone', None)
        position = self.request.query_params.get('position', None)
        
        # 根据参数进行过滤
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        if employee_id:
            queryset = queryset.filter(employee_id__icontains=employee_id)
        
        if phone:
            queryset = queryset.filter(phone__icontains=phone)
        
        if position:
            queryset = queryset.filter(position=position)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        创建教师
        """
        # 过滤掉不需要的字段，只保留可创建的字段
        allowed_fields = [
            'employee_id', 'name', 'gender', 'phone', 'email', 'position', 
            'hire_date', 'notes', 'class_id', 'class_ids', 'kindergarten_id'
        ]
        
        # 创建一个新的字典，只包含允许的字段
        filtered_data = {}
        for field in allowed_fields:
            if field in request.data:
                filtered_data[field] = request.data[field]
        
        serializer = self.get_serializer(data=filtered_data)
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        更新教师信息
        """
        # 过滤掉不需要的字段，只保留可更新的字段
        allowed_fields = [
            'employee_id', 'name', 'gender', 'phone', 'email', 'position', 
            'hire_date', 'notes', 'class_id', 'class_ids'
        ]
        
        # 创建一个新的字典，只包含允许的字段
        filtered_data = {}
        for field in allowed_fields:
            if field in request.data:
                filtered_data[field] = request.data[field]
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=filtered_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def active(self, request):
        """
        获取所有在职教师
        """
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def activate(self, request, pk=None):
        """
        激活教师（恢复在职状态）
        """
        teacher = self.get_object()
        teacher.is_active = True
        teacher.save()
        return Response({'status': 'teacher activated'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def deactivate(self, request, pk=None):
        """
        停用教师（离职状态）
        """
        teacher = self.get_object()
        teacher.is_active = False
        teacher.save()
        return Response({'status': 'teacher deactivated'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def by_position(self, request):
        """
        按职务分组获取教师
        """
        queryset = self.get_queryset()
        position_param = request.query_params.get('position', None)
        
        if position_param:
            queryset = queryset.filter(position=position_param)
        
        # 按职务分组
        result = {}
        for position in ['headmaster', 'deputy_headmaster', 'head_teacher', 'teacher', 'assistant']:
            position_teachers = queryset.filter(position=position, is_active=True)
            result[position] = TeacherBriefSerializer(position_teachers, many=True).data
        
        return Response(result)
    
    @action(detail=False, methods=['post'], permission_classes=[IsKindergartenOwnerOrSystemOwner], parser_classes=[MultiPartParser, FormParser])
    def import_data(self, request):
        """
        批量导入教师数据
        """
        serializer = TeacherImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file = request.FILES['file']
        user = request.user
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file)
            
            # 检查必要的列
            required_columns = ['姓名(*)', '性别(*)', '职位(*)', '手机号码(*)']
            if user.role == 'system_owner':
                required_columns.append('幼儿园名称(*)')
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response(
                    {'error': f'缺少必要的列: {missing_columns}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            created_count = 0
            updated_count = 0
            errors = []
            teachers_to_create = []  # 用于暂存待创建的教师数据
            teachers_to_update = []  # 用于暂存待更新的教师数据
            
            # 预处理所有行数据，收集错误
            processed_data = []
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
                    
                    # 查找是否已存在该教师（通过手机号）
                    teacher = None
                    if '手机号码(*)' in row and pd.notna(row['手机号码(*)']):
                        phone = str(row['手机号码(*)']).strip()
                        teacher = Teacher.objects.filter(phone=phone).first()
                    
                    # 转换职务
                    position_map = {
                        '园长': 'principal',
                        '班主任': 'head_teacher',
                        '配班老师': 'assistant_teacher',
                        '生活老师': 'life_teacher'
                    }
                    position = position_map.get(row['职位(*)'], 'assistant_teacher')
                    
                    # 转换性别
                    gender_map = {
                        '男': 'male',
                        '女': 'female'
                    }
                    gender = gender_map.get(row['性别(*)'], 'female')
                    
                    # 准备教师数据
                    teacher_data = {
                        'name': row['姓名(*)'],
                        'gender': gender,
                        'position': position,
                        'kindergarten_id': kindergarten_id,
                        'phone': phone if pd.notna(row.get('手机号码(*)')) else None
                    }
                    
                    # 处理可选字段
                    optional_fields = {
                        'employee_id': '工号',
                        'email': '邮箱',
                        'notes': '备注'
                    }
                    for field, col in optional_fields.items():
                        if col in row and pd.notna(row[col]):
                            teacher_data[field] = row[col]
                    
                    # 处理班级字段
                    class_id = None
                    if '班级' in row and pd.notna(row['班级']):
                        from classes.models import Class
                        try:
                            class_obj = Class.objects.get(name=row['班级'], kindergarten_id=kindergarten_id)
                            class_id = class_obj.id
                        except Class.DoesNotExist:
                            errors.append(f"第{index+2}行: 班级 '{row['班级']}' 在当前幼儿园中不存在")
                    
                    # 处理入职日期
                    if '入职日期' in row and pd.notna(row['入职日期']):
                        hire_date = row['入职日期']
                        if isinstance(hire_date, pd.Timestamp):
                            hire_date = hire_date.date()
                        teacher_data['hire_date'] = hire_date
                    
                    # 保存处理后的数据
                    processed_data.append({
                        'teacher': teacher,
                        'teacher_data': teacher_data,
                        'class_id': class_id,
                        'row_index': index
                    })
                        
                except Exception as e:
                    errors.append(f"第{index+2}行: {str(e)}")
            
            # 如果有任何错误，直接返回错误信息，不进行任何创建或更新操作
            if errors:
                return Response({
                    'created_count': 0,
                    'updated_count': 0,
                    'total_rows': len(df),
                    'errors': errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 如果没有错误，则执行创建和更新操作
            created_count = 0
            updated_count = 0
            
            for data in processed_data:
                teacher = data['teacher']
                teacher_data = data['teacher_data']
                class_id = data['class_id']
                index = data['row_index']
                
                try:
                    if teacher:
                        # 更新现有教师
                        for field, value in teacher_data.items():
                            setattr(teacher, field, value)
                        teacher.save()
                        # 如果有班级ID，则关联班级
                        if class_id:
                            from classes.models import Class
                            try:
                                class_obj = Class.objects.get(id=class_id)
                                teacher.classes.set([class_obj])
                            except Class.DoesNotExist:
                                pass  # 班级不存在，忽略
                        updated_count += 1
                    else:
                        # 创建新教师
                        new_teacher = Teacher.objects.create(**teacher_data)
                        # 如果有班级ID，则关联班级
                        if class_id:
                            from classes.models import Class
                            try:
                                class_obj = Class.objects.get(id=class_id)
                                new_teacher.classes.add(class_obj)
                            except Class.DoesNotExist:
                                pass  # 班级不存在，忽略
                        created_count += 1
                except Exception as e:
                    # 理论上不应该到这里，但如果发生异常，记录错误
                    errors.append(f"第{index+2}行处理时发生错误: {str(e)}")
            
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
        导出教师数据导入模板
        """
        user = request.user
        
        # 创建模板数据，表头与创建教师字段保持一致
        template_data = {
            '姓名(*)': ['张三', '李四'],
            '工号': ['T001', 'T002'],  # 可选
            '性别(*)': ['女', '男'],
            '职位(*)': ['配班老师', '班主任'],  # 可选值：园长、班主任、配班老师、生活老师
            '手机号码(*)': ['13800138000', '13900139000'],
            '邮箱': ['zhangsan@example.com', 'lisi@example.com'],  # 可选
            '班级': ['大班1', '中班1'],  # 可选，使用班级名称
            '入职日期': ['2023-01-01', '2023-02-01'],  # 可选
            '备注': ['主班老师', '配班老师']  # 可选
        }
        
        # 如果是系统所有者，添加幼儿园名称列
        if user.role == 'system_owner':
            template_data['幼儿园名称(*)'] = ['幼儿园A', '幼儿园B']  # 示例名称
        
        df = pd.DataFrame(template_data)
        
        # 创建响应
        from django.http import HttpResponse
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=teacher_template_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        # 保存到响应
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='教师信息')
        
        return response
    
    @action(detail=False, methods=['get'], permission_classes=[IsKindergartenOwnerOrSystemOwner])
    def stats(self, request):
        """
        获取教师统计信息
        """
        queryset = self.get_queryset()
        
        # 统计总数
        total_count = queryset.count()
        active_count = queryset.filter(is_active=True).count()
        inactive_count = queryset.filter(is_active=False).count()
        
        # 按职务统计
        position_stats = list(queryset.values('position').annotate(count=Count('id')))
        
        # 按性别统计
        gender_stats = list(queryset.values('gender').annotate(count=Count('id')))
        
        # 计算平均每个幼儿园的教师数量
        kindergarten_count = queryset.values('kindergarten_id').distinct().count()
        avg_teachers_per_kindergarten = active_count / kindergarten_count if kindergarten_count > 0 else 0
        
        # 计算平均每个教师负责的学生数量
        total_students = sum(t.get_student_count() for t in queryset.filter(is_active=True))
        avg_students_per_teacher = total_students / active_count if active_count > 0 else 0
        
        # 找出负责班级最多的教师
        teacher_with_most_classes = None
        max_classes = 0
        for teacher in queryset.filter(is_active=True):
            class_count = teacher.get_class_count()
            if class_count > max_classes:
                max_classes = class_count
                teacher_with_most_classes = {
                    'id': teacher.id,
                    'name': teacher.name,
                    'position': teacher.position,
                    'class_count': class_count
                }
        
        # 找出负责学生最多的教师
        teacher_with_most_students = None
        max_students = 0
        for teacher in queryset.filter(is_active=True):
            student_count = teacher.get_student_count()
            if student_count > max_students:
                max_students = student_count
                teacher_with_most_students = {
                    'id': teacher.id,
                    'name': teacher.name,
                    'position': teacher.position,
                    'student_count': student_count
                }
        
        # 统计最近入职的教师（3个月内）
        three_months_ago = timezone.now() - timedelta(days=90)
        recent_hires_count = queryset.filter(hire_date__gte=three_months_ago).count()
        
        # 统计长期在职教师（3年以上）
        three_years_ago = timezone.now() - timedelta(days=3*365)
        long_term_teachers_count = queryset.filter(hire_date__lte=three_years_ago, is_active=True).count()
        
        stats_data = {
            'total_count': total_count,
            'active_count': active_count,
            'inactive_count': inactive_count,
            'position_stats': position_stats,
            'gender_stats': gender_stats,
            'avg_teachers_per_kindergarten': round(avg_teachers_per_kindergarten, 2),
            'avg_students_per_teacher': round(avg_students_per_teacher, 2),
            'teacher_with_most_classes': teacher_with_most_classes,
            'teacher_with_most_students': teacher_with_most_students,
            'recent_hires_count': recent_hires_count,
            'long_term_teachers_count': long_term_teachers_count
        }
        
        serializer = TeacherStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[TeacherDataPermission])
    def class_responsibilities(self, request, pk=None):
        """
        获取教师负责的班级详情
        """
        teacher = self.get_object()
        classes = teacher.classes.filter(is_active=True)
        
        class_details = []
        for class_obj in classes:
            # 统计该班级的学生数量
            try:
                from children.models import Child
                student_count = Child.objects.filter(class_info=class_obj, is_active=True).count()
            except ImportError:
                student_count = 0
            
            # 检查教师在班级中的具体角色
            role = []
            if class_obj.head_teacher and class_obj.head_teacher.id == teacher.id:
                role.append('班主任')
            if class_obj.assistant_teacher and class_obj.assistant_teacher.id == teacher.id:
                role.append('配班老师')
            if class_obj.caregiver and class_obj.caregiver.id == teacher.id:
                role.append('保育员')
            
            class_details.append({
                'class_id': class_obj.id,
                'class_name': class_obj.name,
                'class_type': class_obj.class_type,
                'max_students': class_obj.max_students,
                'current_students': student_count,
                'role': '、'.join(role) if role else '任课教师'
            })
        
        return Response({
            'teacher_id': teacher.id,
            'teacher_name': teacher.name,
            'total_classes': len(class_details),
            'classes': class_details
        })
