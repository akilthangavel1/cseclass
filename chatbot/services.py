import re
from dataclasses import dataclass
from typing import Optional

from django.utils import timezone

from appointments.models import Appointment
from core.models import Department, Doctor


EMAIL_RE = re.compile(r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", re.IGNORECASE)


@dataclass(frozen=True)
class BotReply:
    text: str
    suggested_action: Optional[str] = None


def _extract_email(text: str) -> Optional[str]:
    match = EMAIL_RE.search(text or "")
    return match.group(1) if match else None


def _extract_appointment_id(text: str) -> Optional[int]:
    if not text:
        return None
    candidates = re.findall(r"\b(\d{1,10})\b", text)
    if not candidates:
        return None
    try:
        return int(candidates[0])
    except ValueError:
        return None


def _contains_any(message: str, keywords: list[str]) -> bool:
    return any(k in message for k in keywords)


def generate_bot_reply(user_message: str) -> BotReply:
    msg = (user_message or "").strip()
    lowered = msg.lower()

    if not msg:
        return BotReply("Please type a message and I’ll help.")

    if _contains_any(lowered, ["hi", "hello", "hey", "good morning", "good evening"]):
        return BotReply(
            "Hello. I can help with hospital information, booking appointments, or checking appointment status."
        )

    if _contains_any(lowered, ["emergency", "ambulance", "heart attack", "stroke"]):
        return BotReply(
            "If you believe this is an emergency, call your local emergency number immediately. For non-urgent care, you can book an appointment from the Appointments page."
        )

    if _contains_any(lowered, ["timing", "hours", "open", "closing", "visiting hours"]):
        return BotReply(
            "Our hours are typically Weekdays 08:00–20:00, Saturday 09:00–17:00, Sunday Emergency Only. If you need a specific department’s hours, tell me the department name."
        )

    if _contains_any(lowered, ["location", "address", "where are you", "directions"]):
        return BotReply(
            "We’re located at 123 Wellness Avenue, Downtown, Your City. You can also reach us by phone at +1 (555) 012-3456."
        )

    if _contains_any(lowered, ["department", "departments", "specialties", "specialities"]):
        departments = list(
            Department.objects.filter(is_active=True).order_by("name").values_list("name", flat=True)
        )
        if departments:
            return BotReply(
                "Available departments: " + ", ".join(departments) + ". You can view details on the Departments page."
            )
        return BotReply("Departments are being updated. Please check back soon.")

    if _contains_any(lowered, ["doctor", "doctors", "physician", "specialist"]):
        department = None
        for dept in Department.objects.filter(is_active=True):
            if dept.name.lower() in lowered:
                department = dept
                break
        doctors_qs = Doctor.objects.filter(is_accepting_appointments=True, department__is_active=True).select_related(
            "department"
        )
        if department:
            doctors_qs = doctors_qs.filter(department=department)
        doctors = list(doctors_qs.order_by("full_name")[:8])
        if not doctors:
            return BotReply("No doctors found for that request. You can browse all doctors on the Doctors page.")
        lines = [f"{d.full_name} — {d.specialization} ({d.department.name})" for d in doctors]
        prefix = "Here are some doctors you can book with:\n"
        return BotReply(prefix + "\n".join(lines))

    if _contains_any(lowered, ["book", "booking", "schedule", "appointment", "consultation"]):
        if _contains_any(lowered, ["status", "check status", "track", "confirmed", "pending"]):
            appointment_id = _extract_appointment_id(msg)
            email = _extract_email(msg)
            if not appointment_id and not email:
                return BotReply(
                    "To check status, share your Appointment ID and email address. Example: “status 12 john@example.com”."
                )
            if not appointment_id:
                return BotReply("Please share your Appointment ID (a number).")
            if not email:
                return BotReply("Please share the email address used for the appointment.")
            appointment = (
                Appointment.objects.filter(pk=appointment_id, email=email)
                .select_related("department", "preferred_doctor")
                .first()
            )
            if not appointment:
                return BotReply(
                    "I couldn’t find an appointment with that ID and email. Please double-check and try again."
                )
            when = timezone.localtime(appointment.preferred_datetime).strftime("%Y-%m-%d %H:%M")
            doctor = appointment.preferred_doctor.full_name if appointment.preferred_doctor else "No preference"
            return BotReply(
                f"Appointment #{appointment.pk} status: {appointment.get_status_display()}. Department: {appointment.department.name}. Doctor: {doctor}. Preferred time: {when}."
            )

        return BotReply(
            "You can book an appointment from the Appointment Booking page. If you tell me your department or symptoms, I can suggest a department to start with.",
            suggested_action="book_appointment",
        )

    symptom_map: list[tuple[list[str], str]] = [
        (
            ["fever", "chills", "temperature"],
            "For fever: stay hydrated, rest, and monitor your temperature. Seek urgent care if fever is very high, lasts more than 2–3 days, or you have trouble breathing, severe headache, or confusion.",
        ),
        (
            ["cough", "sore throat", "runny nose", "cold", "flu"],
            "For cough/cold symptoms: rest, fluids, and consider symptomatic relief. Seek care if symptoms worsen, you have chest pain, difficulty breathing, or symptoms persist beyond a week.",
        ),
        (
            ["chest pain", "shortness of breath", "breathless"],
            "Chest pain or shortness of breath can be serious. If symptoms are severe, sudden, or accompanied by sweating, nausea, or fainting, seek emergency care immediately.",
        ),
        (
            ["stomach pain", "abdominal pain", "vomiting", "diarrhea", "nausea"],
            "For stomach issues: hydrate and eat bland foods if tolerated. Seek care if there’s severe pain, blood in vomit/stool, signs of dehydration, or symptoms persist.",
        ),
        (
            ["headache", "migraine", "dizzy", "dizziness"],
            "For headaches/dizziness: rest, hydrate, and avoid triggers. Seek urgent care for sudden severe headache, weakness, vision changes, or confusion.",
        ),
    ]
    for keywords, guidance in symptom_map:
        if _contains_any(lowered, keywords):
            return BotReply(
                guidance
                + "\n\nThis guidance is general information and not a diagnosis. For personalized medical advice, please book an appointment."
            )

    return BotReply(
        "I can help with hospital hours, location, departments, doctors, booking appointments, and checking appointment status. What would you like to do?"
    )

