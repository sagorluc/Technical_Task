from django.contrib import admin
from .models import RepairOrder

class RepairOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "order_id", "customer", "vendor", "variant", "status"]
    ordering = ["-id"]

    
admin.site.register(RepairOrder, RepairOrderAdmin)
