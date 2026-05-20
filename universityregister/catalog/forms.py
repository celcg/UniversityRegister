import datetime

from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .models import ClassGroup, Course, Profesor, Student

STUDENT_GROUP_NAME = 'Students'
PROFESSOR_GROUP_NAME = 'Professors'

def assign_user_role(user, group_name):
    """Assign a newly registered user to exactly one role group."""
    group = Group.objects.get(name=group_name)
    user.groups.set([group])

class UserAccountFieldsMixin:
    """
    Shared username/password fields for registration ModelForms.
    Fields are added in __init__ so templates render inputs, not field objects.
    """

    def _add_user_account_fields(self):
        self.fields['username'] = forms.CharField(
            label='Username',
            max_length=150,
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        )
        self.fields['password1'] = forms.CharField(
            label='Password',
            widget=forms.PasswordInput(attrs={'class': 'form-control'}),
            help_text='Your password must meet Django validation rules.',
        )
        self.fields['password2'] = forms.CharField(
            label='Password confirmation',
            widget=forms.PasswordInput(attrs={'class': 'form-control'}),
            help_text='Enter the same password as before, for verification.',
        )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('A user with that username already exists.'))
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("The two password fields didn't match."))
        if password2:
            validate_password(
                password2,
                User(username=self.cleaned_data.get('username', '')),
            )
        return password2

    def _create_user(self, group_name):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
        )
        assign_user_role(user, group_name)
        return user


class StudentRegistrationForm(UserAccountFieldsMixin, forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'student_id', 'enrollment_year']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'enrollment_year': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_user_account_fields()
        self.order_fields([
            'username', 'password1', 'password2',
            'first_name', 'last_name', 'student_id', 'enrollment_year',
        ])

    def clean_enrollment_year(self):
        year = self.cleaned_data.get('enrollment_year')
        if year is None:
            return year
        current_year = datetime.date.today().year
        if year < current_year - 10 or year > current_year + 1:
            raise ValidationError(
                _('Enter a valid enrollment year (between %(min)s and %(max)s).'),
                params={'min': current_year - 10, 'max': current_year + 1},
            )
        return year

    @transaction.atomic
    def save(self, commit=True):
        user = self._create_user(STUDENT_GROUP_NAME)
        student = super().save(commit=False)
        student.user = user
        if commit:
            student.save()
        return student


class ProfesorRegistrationForm(UserAccountFieldsMixin, forms.ModelForm):
    class Meta:
        model = Profesor
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_user_account_fields()
        self.order_fields(['username', 'password1', 'password2', 'name'])

    @transaction.atomic
    def save(self, commit=True):
        user = self._create_user(PROFESSOR_GROUP_NAME)
        profesor = super().save(commit=False)
        profesor.user = user
        if commit:
            profesor.save()
        return profesor

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

    def __init__(self, *args, **kwargs):
        """
        Custom initialization to restrict status choices.
        This ensures Data Integrity by preventing manual 'FULL' assignment.
        """
        super().__init__(*args, **kwargs)
        
        # Step 1: Check if the 'status' field is present in the form
        if 'status' in self.fields:
            # Step 2: Get all current choices from the Model
            all_choices = self.fields['status'].choices
            
            # Step 3: Create a new list excluding the 'FULL' option
            # 'key' is the database value ('FULL'), 'value' is the human-readable text ('Full')
            self.fields['status'].choices = [
                (key, value) for key, value in all_choices if key != 'FULL'
            ]
