from django import forms
from .models import Submission, Task

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        # These are the only fields the user should fill out
        fields = ['file_upload', 'worker_notes'] 
        
        # Optional: Add widgets for custom styling
        widgets = {
            'worker_notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your notes here...'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to']
        from django import forms
from .models import Suggestion

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['subject', 'content']