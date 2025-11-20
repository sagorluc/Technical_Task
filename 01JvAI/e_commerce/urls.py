
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Google OAuth urls
    path("accounts/", include("allauth.urls")),
    
    # Custom apps urls
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/products/', include('apps.product.urls')),
]
