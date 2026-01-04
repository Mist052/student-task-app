from __future__ import annotations

from django import forms
from django.utils import timezone

from .models import Task, Course, Tag


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class TaskForm(forms.ModelForm):
    due_at = forms.DateTimeField(
        required=False,
        widget=DateTimeLocalInput(attrs={"class": "form-control"}),
        input_formats=["%Y-%m-%dT%H:%M"],
        help_text="Local time (optional).",
    )

    class Meta:
        model = Task
        fields = ["title", "description", "course", "tags", "due_at", "priority", "status"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Finish math homework"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["course"].queryset = Course.objects.filter(owner=self.user)
            self.fields["tags"].queryset = Tag.objects.filter(owner=self.user)

        # When editing an existing Task, populate the datetime-local field
        if self.instance and self.instance.pk and self.instance.due_at:
            # Convert to localtime-like display without timezone suffix
            local_dt = timezone.localtime(self.instance.due_at)
            self.initial["due_at"] = local_dt.strftime("%Y-%m-%dT%H:%M")


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., CS101"}),
            "color": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Reading"}),
        }
