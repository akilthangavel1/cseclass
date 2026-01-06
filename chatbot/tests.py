import json

from django.test import TestCase
from django.urls import reverse

from core.models import Department, Doctor


class ChatbotTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Cardiology")
        Doctor.objects.create(
            full_name="Dr. Alex Morgan",
            department=self.dept,
            specialization="Cardiologist",
            is_accepting_appointments=True,
        )

    def test_chat_page_loads(self):
        res = self.client.get(reverse("chatbot:chat"))
        self.assertEqual(res.status_code, 200)

    def test_chat_api_and_history(self):
        self.client.get(reverse("chatbot:chat"))
        res = self.client.post(
            reverse("chatbot:api_message"),
            data=json.dumps({"message": "departments"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertIn("reply", payload)
        self.assertIn("Cardiology", payload["reply"])

        history = self.client.get(reverse("chatbot:api_history"))
        self.assertEqual(history.status_code, 200)
        items = history.json().get("messages", [])
        self.assertGreaterEqual(len(items), 2)

    def test_chat_api_csrf_cookie_is_set_on_page(self):
        csrf_client = self.client_class(enforce_csrf_checks=True)
        res = csrf_client.get(reverse("chatbot:chat"))
        self.assertEqual(res.status_code, 200)
        token = res.cookies.get("csrftoken").value
        api = csrf_client.post(
            reverse("chatbot:api_message"),
            data=json.dumps({"message": "hours"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(api.status_code, 200)
