from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usermanagement.urls')),
    path('dashboard/', include('accounts.urls')),
    path('', include('movements.urls'))
]
