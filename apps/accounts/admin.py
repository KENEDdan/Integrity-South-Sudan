from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_active", "must_change_password")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Role & Status", {"fields": ("role", "must_change_password", "created_by", "phone_number")}),
    )