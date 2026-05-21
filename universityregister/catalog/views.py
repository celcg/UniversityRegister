from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.db.models import F
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Course, Profesor
from .forms import CourseForm, ClassGroupForm, StudentRegistrationForm, ProfesorRegistrationForm
from .models import Student, Profesor, Course, ClassGroup, Department

def register_view(request):
    """
    Registration page for new students and professors.
    Uses ModelForms with function-view POST binding (forms lecture pattern).
    """
    if request.user.is_authenticated:
        return redirect('index')

    student_form = StudentRegistrationForm()
    profesor_form = ProfesorRegistrationForm()

    if request.method == 'POST':
        if 'submit_student' in request.POST:
            student_form = StudentRegistrationForm(request.POST)
            if student_form.is_valid():
                student = student_form.save()
                login(request, student.user)
                messages.success(
                    request,
                    'Student account created. Welcome!',
                )
                return redirect('student-enroll')

        elif 'submit_profesor' in request.POST:
            profesor_form = ProfesorRegistrationForm(request.POST)
            if profesor_form.is_valid():
                profesor = profesor_form.save()
                login(request, profesor.user)
                messages.success(
                    request,
                    'Professor account created. Welcome!',
                )
                return redirect('profesor-classes')

    return render(request, 'catalog/register.html', {
        'student_form': student_form,
        'profesor_form': profesor_form,
    })


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
    ordering = ['name']

    #For adding search functionality

    def get_queryset(self):
        # getting queryset original
        queryset = super().get_queryset()
        
        # search query from GET parameters
        query = self.request.GET.get('search')
        
        if query:
            # filters profesores by name containing the search query. __icontains makes the search case-insensitive.
            queryset = queryset.filter(name__icontains=query)
            
        return queryset

class ProfesorDetailView(generic.DetailView):
    model = Profesor    

class StudentListView(generic.ListView):
    model = Student
    paginate_by = 3
    ordering = ['first_name', 'last_name']

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
def profesor_create_view(request):
    """
    View for Professors to create new Courses and ClassGroups.
    """
    #  Ensure the user has a Professor profile
    if not hasattr(request.user, 'profesor'):
        # Students should not know the internal creation logic
        raise PermissionDenied

    profesor = request.user.profesor
    # Initialize blank forms for GET requests
    course_form = CourseForm()
    group_form = ClassGroupForm()

    if request.method == 'POST':
        # Logic to distinguish which form was submitted (submit_course vs submit_group)
        if 'submit_course' in request.POST:
            course_form = CourseForm(request.POST)
            if course_form.is_valid():
                # Django validates inputs before saving to DB
                course_form.save()
                return redirect('profesor-create')
        
        elif 'submit_group' in request.POST:
            group_form = ClassGroupForm(request.POST)
            if group_form.is_valid():
                # Save with commit=False to modify the object before writing to DB
                new_group = group_form.save(commit=False)
                # Automatically link the group to the logged-in professor
                new_group.profesor = profesor
                new_group.save()
                return redirect('profesor-classes')

    return render(request, 'catalog/profesor_create.html', {
        'course_form': course_form,
        'group_form': group_form,
    })

@login_required
def profesor_classes_view(request):
    """
    View for Professors to see the ClassGroups they are teaching.
    """
    if not hasattr(request.user, 'profesor'):
        raise PermissionDenied

    #  Filter groups where the 'profesor' field matches the current user
    # Order by date descending to show the newest classes first
    my_groups = ClassGroup.objects.filter(profesor=request.user.profesor).order_by('-start_date')

    return render(request, 'catalog/profesor_classes.html', {
        'my_groups': my_groups,
    })

@login_required
def enroll_class_view(request, pk):

    if not hasattr(request.user, 'student'):
        raise PermissionDenied

    if request.method == 'POST':

        student = request.user.student

        group = get_object_or_404(ClassGroup, pk=pk)

        if student not in group.enrolled_students.all():

            if group.enrolled_students.count() < group.maxStudents:

                # Prevent enrollment in another group of same course
                already_enrolled = student.classes.filter(course=group.course).exists()

                if already_enrolled:
                    messages.warning(
                        request,
                        f'You are already enrolled in another group of {group.course.title}.'
                    )
                    return redirect('student-enroll')
                
                group.enrolled_students.add(student)

                messages.success(
                    request,
                    f'Successfully enrolled in {group.course.title}.'
                )

    return redirect('student-enroll')

@login_required
def student_enroll_view(request):
    """Page for students to enroll ClassGroups"""
    if not hasattr(request.user, 'student'):
        raise PermissionDenied

    #We get all the Courses with ALL their classGroups
    courses = Course.objects.prefetch_related('class_groups')

    return render(request, 'catalog/student_enroll.html', {
        'courses': courses,
    })

@login_required
def student_classes_view(request):
    """Page for students to see their ClassGroups"""
    if not hasattr(request.user, 'student'):
        raise PermissionDenied

    # We get the ClassGroup of this Student
    my_groups = ClassGroup.objects.filter(enrolled_students=request.user.student).order_by('-start_date')

    return render(request, 'catalog/student_classes.html', {
        'my_groups': my_groups,
    })

@login_required
def unenroll_class_view(request, pk):

    if not hasattr(request.user, 'student'):
        raise PermissionDenied

    if request.method == 'POST':

        student = request.user.student

        group = get_object_or_404(ClassGroup, pk=pk)

        # Remove student if enrolled
        if student in group.enrolled_students.all():

            group.enrolled_students.remove(student)

            messages.success(
                request,
                f'You have unenrolled from {group.course.title}.'
            )

    return redirect('student-enroll')