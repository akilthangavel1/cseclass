def site_info(request):
    return {
        "HOSPITAL_NAME": "CityCare General Hospital",
        "HOSPITAL_TAGLINE": "Compassionate care, modern medicine.",
        "HOSPITAL_ADDRESS": "123 Wellness Avenue, Downtown, Your City",
        "HOSPITAL_PHONE": "+1 (555) 012-3456",
        "HOSPITAL_EMAIL": "info@citycare.example",
        "HOSPITAL_HOURS": {
            "Weekdays": "08:00 – 20:00",
            "Saturday": "09:00 – 17:00",
            "Sunday": "Emergency Only",
        },
        "HOSPITAL_EMERGENCY_NOTE": "If this is a medical emergency, call your local emergency number immediately.",
    }

