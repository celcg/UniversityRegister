from django.contrib import admin

# Register your models here.
from .models import Profesor, Level, Department, Course, Student, ClassGroup

# Inlines
class ClassGroupInline(admin.TabularInline):
    """Allows managing Class Groups directly inside the Course or Student page."""
    model = ClassGroup
    extra = 0
    fields = ('class_id', 'start_date', 'status', 'profesor')

class StudentEnrollmentInline(admin.TabularInline):
    """The 'through' model inline for the ManyToMany relationship."""
    model = ClassGroup.enrolled_students.through
    extra = 0
    verbose_name = "Class Enrollment"
    verbose_name_plural = "Class Enrollments"
class ClassGroupProfesorInline(admin.TabularInline):
    model = ClassGroup
    extra = 0  
    fields = ('class_id', 'course', 'start_date', 'status')
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

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'academic_level', 'department')
    list_filter = ('academic_level', 'department')
    search_fields = ('title', 'course_code')
    # Adding ClassGroup inline so you can see all scheduled classes for this course
    inlines = [ClassGroupInline]

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'course', 'status', 'start_date', 'profesor', 'maxStudents')
    list_filter = ('status', 'start_date', 'profesor')
    search_fields = ('class_id','course__title')
    
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

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'last_name', 'first_name', 'enrollment_year')
    list_filter = ('enrollment_year',)
    search_fields = ('last_name', 'first_name', 'student_id')
    # Allows seeing which classes a student is in
    inlines = [StudentEnrollmentInline]

# Simple registrations
@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_total_classes')
    search_fields = ('name',)
    inlines = [ClassGroupProfesorInline]

    # extra column to show the total number of classes a profesor is teaching
    def get_total_classes(self, obj):
        return obj.classes.count()
    
    get_total_classes.short_description = 'Number of Classes'

admin.site.register(Level)