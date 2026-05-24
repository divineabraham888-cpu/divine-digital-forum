from django import forms
from .models import WorkerSubmission, Task

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = WorkerSubmission
        fields = ['title', 'submission_type', 'content', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to'] # Ensure these match models.py