from django.contrib import admin

from .models import ContactMessage, Department, Doctor


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["full_name", "specialization", "department", "is_accepting_appointments"]
    list_filter = ["department", "is_accepting_appointments"]
    search_fields = ["full_name", "specialization", "bio", "department__name"]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["created_at", "name", "email", "subject", "status"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    list_editable = ["status"]
