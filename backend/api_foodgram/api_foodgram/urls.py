from django.contrib import admin
from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView


urlpatterns = [
    # re_path('^auth/', include('djoser.urls')),
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
]
