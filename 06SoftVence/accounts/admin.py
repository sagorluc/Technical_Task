from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "role", "is_active", "is_staff", "is_superuser"]
    ordering = ["-id"]

    
admin.site.register(User, UserAdmin)