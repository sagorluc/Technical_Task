from django.contrib import admin
from .models import Service, ServiceVariant

class ServiceAdmin(admin.ModelAdmin):
    list_display = ["id", "vendor", "name"]
    ordering = ["-id"]

class ServiceVariantAdmin(admin.ModelAdmin):
    list_display = ["id", "service", "name", "price"]
    ordering = ["-id"]
    
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceVariant, ServiceVariantAdmin)
