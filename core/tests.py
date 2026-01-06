from django.test import TestCase
from django.urls import reverse

from .models import Department, Doctor


class PublicPagesTests(TestCase):
    def test_core_pages_load(self):
        for name in ["core:home", "core:about", "core:departments", "core:doctors", "core:contact"]:
            res = self.client.get(reverse(name))
            self.assertEqual(res.status_code, 200)

    def test_departments_and_doctors_render(self):
        dept = Department.objects.create(name="Cardiology", description="Heart care")
        Doctor.objects.create(
            full_name="Dr. Alex Morgan",
            department=dept,
            specialization="Cardiologist",
            availability="Mon–Fri 10:00–16:00",
            is_accepting_appointments=True,
        )
        res = self.client.get(reverse("core:departments"))
        self.assertContains(res, "Cardiology")
        res2 = self.client.get(reverse("core:doctors"))
        self.assertContains(res2, "Dr. Alex Morgan")
