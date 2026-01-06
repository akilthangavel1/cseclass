from django.db import models
from django.utils import timezone

from core.models import Department, Doctor


class Appointment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
    ]

    patient_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    preferred_doctor = models.ForeignKey(
        Doctor, on_delete=models.SET_NULL, null=True, blank=True
    )
    preferred_datetime = models.DateTimeField()
    symptoms = models.TextField(blank=True)
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Appointment #{self.pk} — {self.patient_name}"

    @property
    def is_past(self) -> bool:
        return self.preferred_datetime < timezone.now()
