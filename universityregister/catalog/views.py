from django.shortcuts import render, redirect
from django.db.models import Q
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Course, Profesor
from .forms import CourseForm, ClassGroupForm
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


@login_required
def profesor_dashboard(request):
    # Step 1: Authorization check
    # We verify if the logged-in user has a 'Profesor' profile linked to their account
    if not hasattr(request.user, 'profesor'):
        # If not a professor, we raise a 403 Forbidden error (Confidentiality principle)
        raise PermissionDenied 

    profesor = request.user.profesor

    # Step 2: Data Retrieval (Integrity)
    # Get only the courses taught by this specific professor
    # We use distinct() to avoid duplicate entries in the list
    my_courses = Course.objects.filter(class_groups__profesor=profesor).distinct()

    # Step 3: Handle the 'Create New Course' form
    if request.method == 'POST':
        # If the user submitted the form, we process the data
        form = CourseForm(request.POST)
        if form.is_valid():
            # Save the new course to the database
            form.save()
            # Redirect to the same page to see the updated list
            return redirect('profesor-dashboard')
    else:
        # If it's a GET request, we just show an empty form
        form = CourseForm()

    context = {
        'my_courses': my_courses,
        'form': form,
    }
    return render(request, 'catalog/profesor_dashboard.html', context)
@login_required
def profesor_create_view(request):
    """Página para que el profesor cree nuevos Cursos y ClassGroups"""
    if not hasattr(request.user, 'profesor'):
        raise PermissionDenied

    profesor = request.user.profesor
    course_form = CourseForm()
    group_form = ClassGroupForm()

    if request.method == 'POST':
        if 'submit_course' in request.POST:
            course_form = CourseForm(request.POST)
            if course_form.is_valid():
                course_form.save()
                return redirect('profesor-create')
        
        elif 'submit_group' in request.POST:
            group_form = ClassGroupForm(request.POST)
            if group_form.is_valid():
                new_group = group_form.save(commit=False)
                new_group.profesor = profesor
                new_group.save()
                return redirect('profesor-classes') # Redirigir a la vista de lista

    return render(request, 'catalog/profesor_create.html', {
        'course_form': course_form,
        'group_form': group_form,
    })

@login_required
def profesor_classes_view(request):
    """Página para que el profesor vea sus ClassGroups actuales"""
    if not hasattr(request.user, 'profesor'):
        raise PermissionDenied

    # Obtenemos los grupos de clase asignados a este profesor
    my_groups = ClassGroup.objects.filter(profesor=request.user.profesor).order_by('-start_date')

    return render(request, 'catalog/profesor_classes.html', {
        'my_groups': my_groups,
    })