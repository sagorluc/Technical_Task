from django.contrib import admin
from .models import Payment, PaymentEvent

class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "intent_id", "status"]
    ordering = ["-id"]

class PaymentEventAdmin(admin.ModelAdmin):
    list_display = ["id", "payment", "event_id", "processed"]
    ordering = ["-id"]
    
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentEvent, PaymentEventAdmin)
