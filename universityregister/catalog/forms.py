from django import forms
from .models import ClassGroup, Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'title', 'description', 'academic_level', 'department', 'topic']
        
        # We apply 'form-control' to EVERY field to fix the layout
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'academic_level': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            
        }
class ClassGroupForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
        # We exclude 'profesor' because we will assign it automatically in the view
        fields = ['class_id', 'course', 'start_date', 'end_date', 'status', 'schedule', 'maxStudents']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'schedule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mon/Wed 10:00'}),
            'class_id': forms.TextInput(attrs={'class': 'form-control'}),
            'maxStudents': forms.NumberInput(attrs={'class': 'form-control'}),
        }