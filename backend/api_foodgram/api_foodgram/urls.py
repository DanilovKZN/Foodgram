from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # re_path('^auth/', include('djoser.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
]
