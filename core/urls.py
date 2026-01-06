from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("@vite/client", views.vite_client, name="vite_client"),
    path("@vite/client/", views.vite_client),
    path("about/", views.about, name="about"),
    path("departments/", views.departments, name="departments"),
    path("doctors/", views.doctors, name="doctors"),
    path("contact/", views.contact, name="contact"),
]
