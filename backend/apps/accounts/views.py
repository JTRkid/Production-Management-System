"""用户认证与管理视图"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Workshop, OperationLog
from .serializers import (
    LoginSerializer, UserSerializer, UserCreateSerializer,
    ChangePasswordSerializer, WorkshopSerializer, OperationLogSerializer,
)


def get_tokens_for_user(user):
    """为指定用户生成 JWT access/refresh token 对"""
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }


def get_client_ip(request):
    """获取客户端真实 IP，优先取 X-Forwarded-For 头"""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class LoginViewSet(viewsets.ViewSet):
    """处理用户登录与密码修改，无需认证即可访问"""

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @action(methods=['post'], detail=False)
    def login(self, request):
        """用户登录：验证凭据并返回 JWT token 和用户基本信息"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)

        OperationLog.objects.create(
            user=user, action='login', target='系统登录',
            ip_address=get_client_ip(request),
        )

        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                **tokens,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'role': user.role,
                    'phone': user.phone,
                },
            },
        })

    @action(methods=['post'], detail=False)
    def change_password(self, request):
        """修改密码：校验旧密码后设置新密码"""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.data['old_password']):
            return Response({'code': 400, 'message': '旧密码错误'}, status=400)
        user.set_password(serializer.data['new_password'])
        user.save()
        return Response({'code': 200, 'message': '密码修改成功，请重新登录'})


class UserViewSet(viewsets.ModelViewSet):
    """管理系统用户：增删改查、重置密码、启用/禁用"""

    queryset = User.objects.all()
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'name', 'phone']
    ordering_fields = ['date_joined', 'username']

    def get_serializer_class(self):
        """创建时使用 UserCreateSerializer（含密码字段），其余使用 UserSerializer"""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['post'], detail=True)
    def reset_password(self, request, pk=None):
        """重置指定用户的密码为默认值 123456"""
        user = self.get_object()
        user.set_password('123456')
        user.save()
        OperationLog.objects.create(
            user=request.user, action='update', target=f'重置密码-{user.username}',
            ip_address=get_client_ip(request),
        )
        return Response({'code': 200, 'message': '密码已重置为 123456'})

    @action(methods=['post'], detail=True)
    def toggle_active(self, request, pk=None):
        """切换用户的启用/禁用状态"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        OperationLog.objects.create(
            user=request.user, action='update',
            target=f"{'启用' if user.is_active else '禁用'}用户-{user.username}",
            ip_address=get_client_ip(request),
        )
        return Response({'code': 200, 'message': '状态已更新'})


class WorkshopViewSet(viewsets.ModelViewSet):
    """管理车间信息：增删改查"""

    queryset = Workshop.objects.all()
    serializer_class = WorkshopSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """操作日志（只读）：记录用户登录、数据变更等操作"""

    queryset = OperationLog.objects.select_related('user').all()
    serializer_class = OperationLogSerializer
    filterset_fields = ['action']
    search_fields = ['target']
    ordering_fields = ['-created_at']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})
