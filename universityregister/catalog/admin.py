from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth import get_user_model
# Register your models here.
from .models import Profesor, Level, Department, Course, Student, ClassGroup, User

from django.contrib.auth.admin import UserAdmin

User = get_user_model()

if admin.site.is_registered(User):
    admin.site.unregister(User)
admin.site.register(User, UserAdmin)

#LEVEL
admin.site.register(Level)

#DEPARTMENT
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'head_of_department', 'building_location')
    # Organizing the department edit form
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Administration', {
            'fields': ('head_of_department', 'building_location'),
        }),
    )

#COURSE
class ClassGroupInline(admin.TabularInline):
    """Allows managing Class Groups directly inside the Course page."""
    model = ClassGroup
    extra = 0
    fields = ('class_id', 'start_date', 'status', 'profesor')
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'academic_level', 'department')
    list_filter = ('academic_level', 'department')
    search_fields = ('title', 'course_code', 'class_groups__class_id')
    fields = [
        ('course_code', 'title'),
        'academic_level',
        ('topic', 'description'), 'department' 
    ]
    # Adding ClassGroup inline so you can see all scheduled classes for this course
    inlines = [ClassGroupInline]

#STUDENT
# Proxy model for giving a nice __str__ to the intermediate table
class EnrollmentProxy(ClassGroup.enrolled_students.through):
    class Meta:
        proxy = True # This tells Django this is just a proxy for the existing model, not a new table

    def __str__(self):
        return f"{self.classgroup}"

class StudentEnrollmentInline(admin.TabularInline):
    """Allows managing Class Groups directly inside the Student page."""
    model = EnrollmentProxy       # Using the proxy model to have a better string representation in the admin
    extra = 1
    verbose_name = "Class Enrollment"
    verbose_name_plural = "Class Enrollments"
    
# ALTERNATIVE WITHOUT PROXY
# class StudentEnrollmentInline(admin.TabularInline):
#     """Allows managing Class Groups directly inside the Student page."""
#     model = ClassGroup.enrolled_students.through
#     extra = 1
#     verbose_name = "Class Enrollment"
#     verbose_name_plural = "Class Enrollments"

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'last_name', 'first_name', 'enrollment_year')
    list_filter = ('enrollment_year',)
    search_fields = ('last_name', 'first_name', 'student_id', 'user__username')
    # Allows seeing which classes a student is in
    inlines = [StudentEnrollmentInline]
    
    # search based on the username of the related User model
    raw_id_fields = ('user',)

#PROFESOR
class ClassGroupProfesorInline(admin.TabularInline):
    """Allows managing Class Groups directly inside the Profesor page."""
    model = ClassGroup
    extra = 0  
    fields = ('class_id', 'course', 'start_date', 'status')

@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'get_total_classes') 
    search_fields = ('name', 'user__username')
    inlines = [ClassGroupProfesorInline]
    # search based on the username of the related User model
    raw_id_fields = ('user',)
    # extra column to show the total number of classes a profesor is teaching
    @admin.display(description='Number of Classes')
    def get_total_classes(self, obj):
        return obj.classes.count()
#CLASS GROUP
class ClassGroupAdminForm(forms.ModelForm):

    class Meta:
        model = ClassGroup
        fields = '__all__'

    def clean(self):

        cleaned_data = super().clean()

        students = cleaned_data.get('enrolled_students')
        max_students = cleaned_data.get('maxStudents')

        if students and max_students:

            #First we check if the number of students enrolled is more than the maximum
            if students.count() > max_students:

                raise ValidationError(
                    f"You cannot enroll more than {max_students} students."
                )
            
            #Now we make sure that you can not enroll a student in two diferent groups of the same course
            course = cleaned_data.get('course')
            for student in students:

                existing_groups = student.classes.filter(course=course)

                # Exclude current group when editing
                if self.instance.pk:
                    existing_groups = existing_groups.exclude(pk=self.instance.pk)

                if existing_groups.exists():

                    raise ValidationError(
                        f"{student} is already enrolled in another group of this course."
                    )

        return cleaned_data
    
@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'course', 'get_computed_status', 'start_date', 'profesor', 'maxStudents')
    list_filter = ('status', 'start_date', 'profesor')
    search_fields = ('class_id','course__title')

    form = ClassGroupAdminForm
    
    # Dual-pane selection for students
    filter_horizontal = ('enrolled_students',) 
    
    fieldsets = (
        ('General Info', {
            'fields': ('class_id', 'course', 'profesor')
        }),
        ('Schedule & Status', {
            'fields': ('status', 'schedule', ('start_date', 'end_date'))
        }),
        ('Capacity', {
            'fields': ('maxStudents',),
            'description': 'Set the limit of students for this specific group.'
        }),
        ('Enrollment', {
            'fields': ('enrolled_students',), # WHERE to display the field of filter_horizontal
        }),
    )

    def get_computed_status(self, obj):
        return obj.computed_status

    get_computed_status.short_description = 'Status'




