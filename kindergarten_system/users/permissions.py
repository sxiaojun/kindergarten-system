from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """
    仅允许对象所有者或只读操作
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user

class IsSystemOwner(BasePermission):
    """
    仅允许系统所有者访问
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'owner'

class IsKindergartenOwner(BasePermission):
    """
    仅允许园长访问
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'principal'

class IsTeacher(BasePermission):
    """
    仅允许教师访问
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'teacher'

class IsKindergartenOwnerOrSystemOwner(BasePermission):
    """
    允许园长、系统所有者和教师访问
    """
    def has_permission(self, request, view):
        return (hasattr(request.user, 'role') and 
                (request.user.role == 'owner' or 
                 request.user.role == 'principal' or
                 request.user.role == 'teacher'))

class IsAuthenticatedAndHasRole(BasePermission):
    """
    验证用户是否已认证且有角色
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                hasattr(request.user, 'role') and 
                request.user.role is not None)

class KindergartenDataPermission(BasePermission):
    """
    控制幼儿园数据访问权限：
    - 系统所有者可以访问所有数据
    - 园长只能访问自己幼儿园的数据
    - 教师只能访问自己关联班级的数据
    """
    def has_object_permission(self, request, view, obj):
        # 系统所有者可以访问所有数据
        if hasattr(request.user, 'role') and request.user.role == 'owner':
            return True
        
        # 园长只能访问自己幼儿园的数据
        if hasattr(request.user, 'role') and request.user.role == 'principal':
            if hasattr(obj, 'kindergarten'):
                return obj.kindergarten == request.user.kindergarten
            # 如果对象本身是幼儿园，则检查是否是自己的幼儿园
            if hasattr(obj, 'id') and hasattr(request.user, 'kindergarten'):
                return obj.id == request.user.kindergarten.id
        
        # 教师只能访问自己关联班级的数据
        if hasattr(request.user, 'role') and request.user.role == 'teacher':
            if hasattr(obj, 'class'):
                return obj.classes in request.user.classes.all()
            if hasattr(obj, 'classes'):
                return obj.classes.filter(id__in=[c.id for c in request.user.classes.all()]).exists()
            if hasattr(obj, 'kindergarten'):
                return obj.kindergarten == request.user.kindergarten
        
        return False
    
    def has_permission(self, request, view):
        # 所有已认证且有角色的用户都可以访问列表视图
        # 具体的对象级权限在has_object_permission中检查
        return IsAuthenticatedAndHasRole().has_permission(request, view)

class TeacherDataPermission(BasePermission):
    """
    教师数据访问权限：
    - 系统所有者可以访问所有数据
    - 园长只能访问自己幼儿园的教师数据
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'role'):
            if request.user.role == 'owner':
                return True
            elif request.user.role == 'principal':
                return obj.kindergarten == request.user.kindergarten
        return False

class ClassDataPermission(BasePermission):
    """
    班级数据访问权限：
    - 系统所有者可以访问所有数据
    - 园长只能访问自己幼儿园的班级数据
    - 教师只能访问自己负责的班级数据
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'role'):
            if request.user.role == 'owner':
                return True
            elif request.user.role == 'principal':
                return obj.kindergarten == request.user.kindergarten
            elif request.user.role == 'teacher' and hasattr(request.user, 'teacher'):
                # 检查班级是否在教师负责的班级列表中
                return obj in request.user.teacher.classes.all()
        return False

class ChildDataPermission(BasePermission):
    """
    幼儿数据访问权限：
    - 系统所有者可以访问所有数据
    - 园长只能访问自己幼儿园的幼儿数据
    - 教师只能访问自己关联班级的幼儿数据
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'role'):
            if request.user.role == 'owner':
                return True
            elif request.user.role == 'principal':
                return obj.kindergarten == request.user.kindergarten
            elif request.user.role == 'teacher' and hasattr(request.user, 'teacher'):
                # 检查幼儿所在的班级是否在教师负责的班级列表中
                return obj.class_info in request.user.teacher.classes.all()
        return False