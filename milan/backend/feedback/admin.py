from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Feedback

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_manager', 'manager')
    list_filter = ('is_manager', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('is_manager', 'manager')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('is_manager', 'manager')}),
    )

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('employee', 'manager', 'sentiment', 'acknowledged', 'created_at')
    list_filter = ('sentiment', 'acknowledged', 'created_at')
    search_fields = ('employee__username', 'manager__username', 'strengths', 'areas_to_improve')
    readonly_fields = ('created_at', 'updated_at', 'acknowledged_at')
