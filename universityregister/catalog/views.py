from django.shortcuts import render

# Create your views here.

from .models import Student, Profesor, Course, ClassGroup, Department

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_students = Student.objects.count()
    num_profesores = Profesor.objects.count()
    num_courses = Course.objects.count()
    num_departments = Department.objects.count()
    num_classgroups = ClassGroup.objects.count()

    # Open clases (status = '  OPEN')
    num_classgroups_open = ClassGroup.objects.filter(status__exact='OPEN').count()

    context = {
        'num_students': num_students,
        'num_profesores': num_profesores,
        'num_courses': num_courses,
        'num_departments': num_departments,
        'num_classgroups': num_classgroups,
        'num_classgroups_open': num_classgroups_open,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)