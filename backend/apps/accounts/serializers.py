"""用户与账号序列化器"""

import re
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Workshop, OperationLog


class LoginSerializer(serializers.Serializer):
    """登录请求序列化器：验证用户名和密码"""

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        from django.contrib.auth import authenticate
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器（不含密码），用于列表和详情展示"""

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'role', 'phone', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器：包含密码字段，创建时自动加密"""

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'name', 'password', 'role', 'phone']

    def create(self, validated_data):
        # 将明文密码加密后再存入数据库
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器：校验旧密码和新密码"""

    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)


class WorkshopSerializer(serializers.ModelSerializer):
    """车间信息序列化器：包含负责人姓名（只读）"""

    # 关联字段：自动获取车间负责人的姓名
    manager_name = serializers.CharField(source='manager.name', read_only=True)

    class Meta:
        model = Workshop
        fields = '__all__'
        read_only_fields = ['created_at']


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器：包含操作人姓名（只读）"""

    # 关联字段：自动获取操作人的姓名
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = OperationLog
        fields = '__all__'
