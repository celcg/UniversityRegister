from django.contrib import admin

# Register your models here.
from .models import Profesor, Level, Department, Course, Student, ClassGroup

admin.site.register(Profesor)
admin.site.register(Level)
admin.site.register(Department)
admin.site.register(Course)
#admin.site.register(Student)
#admin.site.register(ClassGroup)

# 1. Viewing Students inside the ClassGroup Admin
@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'course', 'start_date', 'status', 'profesor')
    # This creates a dual-pane selection widget for the enrolled_students ManyToMany field
    filter_horizontal = ('enrolled_students',) 


# 2. Viewing Classes inside the Student Admin
# We use the automatically created "through" model for the ManyToMany relationship
class ClassGroupInline(admin.TabularInline):
    model = ClassGroup.enrolled_students.through
    extra = 0 # Prevents empty blank rows from showing up by default
    verbose_name = "Class Enrollment"
    verbose_name_plural = "Class Enrollments"

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'student_id', 'enrollment_year')
    search_fields = ('first_name', 'last_name', 'student_id')
    # This adds the classes directly to the Student edit page
    inlines = [ClassGroupInline]