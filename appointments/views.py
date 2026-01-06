from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from core.models import Department, Doctor

from .forms import AppointmentBookingForm, AppointmentStatusCheckForm
from .models import Appointment


def book_appointment(request):
    if request.method == "POST":
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            return render(
                request,
                "appointments/appointment_success.html",
                {"appointment": appointment},
            )
        messages.error(request, "Please correct the highlighted errors and try again.")
    else:
        form = AppointmentBookingForm()

    departments = Department.objects.filter(is_active=True).order_by("name")
    return render(
        request,
        "appointments/book_appointment.html",
        {"form": form, "departments": departments},
    )


def appointment_status_checker(request):
    result = None
    if request.method == "POST":
        form = AppointmentStatusCheckForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            appointment_id = form.cleaned_data["appointment_id"]
            appointment = Appointment.objects.filter(pk=appointment_id, email=email).select_related(
                "department", "preferred_doctor"
            ).first()
            if appointment:
                result = {"found": True, "appointment": appointment}
            else:
                result = {"found": False}
                messages.error(
                    request,
                    "No appointment found with that email and ID. Please double-check and try again.",
                )
    else:
        form = AppointmentStatusCheckForm()

    return render(
        request,
        "appointments/appointment_status.html",
        {"form": form, "result": result},
    )


@require_GET
def doctors_for_department(request):
    department_id = request.GET.get("department_id", "").strip()
    if not department_id.isdigit():
        return JsonResponse({"doctors": []})
    doctors = (
        Doctor.objects.filter(
            department_id=int(department_id),
            is_accepting_appointments=True,
            department__is_active=True,
        )
        .order_by("full_name")
        .values("id", "full_name", "specialization")
    )
    return JsonResponse({"doctors": list(doctors)})
