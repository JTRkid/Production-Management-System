from django.contrib import admin
from .models import User, Workshop, OperationLog

admin.site.register(User)
admin.site.register(Workshop)
admin.site.register(OperationLog)
