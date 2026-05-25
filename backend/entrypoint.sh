#!/bin/bash
set -e

echo "==> 收集静态文件..."
python manage.py collectstatic --noinput

echo "==> 运行数据库迁移..."
python manage.py migrate --noinput

echo "==> 填充种子数据..."
python seed_data.py || echo "种子数据已存在，跳过"

echo "==> 启动 Gunicorn (Uvicorn worker)..."
exec gunicorn teach_platform.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
