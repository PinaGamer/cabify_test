from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('checkout/', include('checkout_app.urls')),
    path('admin/', admin.site.urls),
]
