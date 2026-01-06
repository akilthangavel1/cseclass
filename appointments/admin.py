from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "created_at",
        "patient_name",
        "email",
        "phone",
        "department",
        "preferred_doctor",
        "preferred_datetime",
        "status",
    ]
    list_filter = ["status", "department", "preferred_doctor", "created_at"]
    search_fields = ["patient_name", "email", "phone", "symptoms"]
    list_editable = ["status"]
    readonly_fields = ["created_at"]
