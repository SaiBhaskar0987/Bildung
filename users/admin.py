from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'first_name', 'last_name', 'role', 'is_active')}),
    )

    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')

    def save_model(self, request, obj, form, change):
        if not change:  
            obj.is_active = False  
        super().save_model(request, obj, form, change)