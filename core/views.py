from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import ContactForm
from .models import Department, Doctor


def home(request):
    departments = (
        Department.objects.filter(is_active=True)
        .annotate(doctor_count=Count("doctors"))
        .order_by("name")[:6]
    )
    doctors = Doctor.objects.filter(is_accepting_appointments=True).select_related(
        "department"
    )[:6]
    return render(
        request,
        "core/home.html",
        {
            "departments": departments,
            "doctors": doctors,
        },
    )


def about(request):
    return render(request, "core/about.html")


def departments(request):
    qs = (
        Department.objects.filter(is_active=True)
        .annotate(doctor_count=Count("doctors"))
        .order_by("name")
    )
    return render(request, "core/departments.html", {"departments": qs})


def doctors(request):
    department_slug = request.GET.get("department", "").strip()
    departments_qs = Department.objects.filter(is_active=True).order_by("name")

    doctors_qs = (
        Doctor.objects.select_related("department")
        .filter(department__is_active=True)
        .order_by("full_name")
    )
    selected_department = None
    if department_slug:
        selected_department = departments_qs.filter(slug=department_slug).first()
        if selected_department:
            doctors_qs = doctors_qs.filter(department=selected_department)

    return render(
        request,
        "core/doctors.html",
        {
            "departments": departments_qs,
            "doctors": doctors_qs,
            "selected_department": selected_department,
        },
    )


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out. We will respond shortly.")
            return redirect("core:contact")
        messages.error(request, "Please correct the highlighted errors and try again.")
    else:
        form = ContactForm()

    return render(request, "core/contact.html", {"form": form})


def vite_client(request):
    return HttpResponse("", content_type="application/javascript", status=204)
