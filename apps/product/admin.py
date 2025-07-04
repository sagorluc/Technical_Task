from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "category", "name", "price")
    list_filter = ("category",)
    search_fields = ("name", "description")
    ordering = ("-created_at",)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")