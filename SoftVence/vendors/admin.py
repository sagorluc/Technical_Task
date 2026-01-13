from django.contrib import admin
from .models import Vendor

class VendorAdmin(admin.ModelAdmin):
    list_display = ["id", "business_name", "is_active"]
    ordering = ["-id"]
    
admin.site.register(Vendor, VendorAdmin)
