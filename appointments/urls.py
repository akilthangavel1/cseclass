from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    path("appointments/book/", views.book_appointment, name="book"),
    path("appointments/status/", views.appointment_status_checker, name="status"),
    path("appointments/doctors/", views.doctors_for_department, name="doctors_for_department"),
]

