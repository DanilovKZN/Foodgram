from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    model = CustomUser
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'is_blocked',
    )
    search_fields = ('username', 'first_name',)
    list_filter = ('username', 'email',)
    list_editable = ('is_blocked',)
    empty_value_display = '-пусто-'
    list_per_page = 10
