from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Department, Doctor

from .models import Appointment


class AppointmentFlowTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Dermatology")
        self.doctor = Doctor.objects.create(
            full_name="Dr. Priya Shah",
            department=self.dept,
            specialization="Dermatologist",
            is_accepting_appointments=True,
        )

    def test_booking_creates_appointment(self):
        when = (timezone.now() + timezone.timedelta(days=1)).replace(second=0, microsecond=0)
        res = self.client.post(
            reverse("appointments:book"),
            data={
                "patient_name": "Jordan Lee",
                "email": "jordan@example.com",
                "phone": "1234567890",
                "department": self.dept.id,
                "preferred_doctor": self.doctor.id,
                "preferred_datetime": when.strftime("%Y-%m-%dT%H:%M"),
                "symptoms": "Rash",
            },
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 1)
        appt = Appointment.objects.first()
        self.assertContains(res, f"#{appt.id}")

    def test_status_checker_finds_appointment(self):
        appt = Appointment.objects.create(
            patient_name="Jordan Lee",
            email="jordan@example.com",
            phone="1234567890",
            department=self.dept,
            preferred_doctor=self.doctor,
            preferred_datetime=(timezone.now() + timezone.timedelta(days=1)),
            symptoms="Rash",
        )
        res = self.client.post(
            reverse("appointments:status"),
            data={"email": "jordan@example.com", "appointment_id": appt.id},
        )
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Status")
        self.assertContains(res, f"#{appt.id}")
