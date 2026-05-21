#!/bin/bash
set -e

echo "==> 运行数据库迁移..."
python manage.py migrate --noinput

echo "==> 填充种子数据..."
python seed_data.py || echo "种子数据已存在，跳过"

echo "==> 启动 Gunicorn..."
exec gunicorn teach_platform.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 60 \
    --access-logfile -
