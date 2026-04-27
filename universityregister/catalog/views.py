from django.shortcuts import render
from django.db.models import Q
from django.db.models import F

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

    # For showing the last visited course
    last_course = None
    last_course_id = request.session.get('last_course_id')

    if last_course_id:
        last_course = Course.objects.filter(id=last_course_id).first()

    # For showing the course ranking. Top 3
    top_courses = Course.objects.order_by('-visit_count')[:3]

    context = {
        'num_students': num_students,
        'num_profesores': num_profesores,
        'num_courses': num_courses,
        'num_departments': num_departments,
        'num_classgroups': num_classgroups,
        'num_classgroups_open': num_classgroups_open,
        'last_course': last_course,
        'top_courses': top_courses,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

from django.views import generic

class CourseListView(generic.ListView):
    model = Course
    paginate_by = 10
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search')
        
        if query:
            # Filtra si el título O el código del curso contienen la palabra
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(course_code__icontains=query)
            )
            
        return queryset

class CourseDetailView(generic.DetailView):
    model = Course

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # We store the id of this course in the session
        self.request.session['last_course_id'] = obj.id

        # We update the global counter from the DB using F()
        obj.visit_count = F('visit_count') + 1
        obj.save()
        obj.refresh_from_db()

        return obj


class ProfesorListView(generic.ListView):
    model = Profesor
    paginate_by = 2

    #For adding search functionality

    def get_queryset(self):
        # Obtenemos el queryset original
        queryset = super().get_queryset()
        
        # Buscamos si hay un parámetro 'search' en la URL
        query = self.request.GET.get('search')
        
        if query:
            # Filtramos por el campo 'name' (ajusta si el campo se llama distinto)
            queryset = queryset.filter(name__icontains=query)
            
        return queryset

class ProfesorDetailView(generic.DetailView):
    model = Profesor    

class StudentListView(generic.ListView):
    model = Student
    paginate_by = 3
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search')
        
        if query:
            # filters students by first name or last name containing the search query. Q objects allow for complex queries with OR conditions.
            queryset = queryset.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )
            
        return queryset

class StudentDetailView(generic.DetailView):
    model = Student