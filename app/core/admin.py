from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name', 'is_active']
    fieldsets = (
        (_('User Credentials'), {'fields': ('email', 'password')}),
        (_('Personal Details'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


class CategoryAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['name', 'user']

class PostAdmin(admin.ModelAdmin):
    ordering = ['date_posted']
    list_display = ['title', 'date_posted', 'author']

class TagAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['name','user']

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Post,PostAdmin )
