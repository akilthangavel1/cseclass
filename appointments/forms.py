from django import forms
from django.utils import timezone

from core.models import Department, Doctor

from .models import Appointment


class AppointmentBookingForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True), empty_label="Select a department"
    )
    preferred_doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_accepting_appointments=True),
        required=False,
        empty_label="No preference",
    )

    class Meta:
        model = Appointment
        fields = [
            "patient_name",
            "email",
            "phone",
            "department",
            "preferred_doctor",
            "preferred_datetime",
            "symptoms",
        ]
        widgets = {
            "preferred_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "symptoms": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs["class"] = f"select {widget.attrs.get('class', '')}".strip()
            else:
                widget.attrs["class"] = f"input {widget.attrs.get('class', '')}".strip()

        self.fields["patient_name"].widget.attrs.setdefault("autocomplete", "name")
        self.fields["email"].widget.attrs.setdefault("autocomplete", "email")
        self.fields["phone"].widget.attrs.setdefault("autocomplete", "tel")
        self.fields["preferred_datetime"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]

    def clean_preferred_datetime(self):
        value = self.cleaned_data["preferred_datetime"]
        if value <= timezone.now():
            raise forms.ValidationError("Please choose a future date and time.")
        return value

    def clean(self):
        cleaned = super().clean()
        department = cleaned.get("department")
        preferred_doctor = cleaned.get("preferred_doctor")
        if department and preferred_doctor and preferred_doctor.department_id != department.id:
            self.add_error(
                "preferred_doctor", "Please choose a doctor from the selected department."
            )
        return cleaned


class AppointmentStatusCheckForm(forms.Form):
    email = forms.EmailField()
    appointment_id = forms.IntegerField(min_value=1, label="Appointment ID")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = f"input {field.widget.attrs.get('class', '')}".strip()
        self.fields["email"].widget.attrs.setdefault("autocomplete", "email")
