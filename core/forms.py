from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            base_class = "input"
            if widget.__class__.__name__.lower().endswith("select"):
                base_class = "select"
            if widget.__class__.__name__.lower().endswith("textarea"):
                base_class = "input"
            widget.attrs["class"] = f"{base_class} {widget.attrs.get('class', '')}".strip()

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 6}),
        }
