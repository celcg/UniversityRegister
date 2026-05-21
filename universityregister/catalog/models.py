from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User  # import User model for connecting with Profesor and Student


class Profesor(models.Model):
  """Model representing a profesor."""
  user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
  name = models.CharField(max_length=200, help_text='Enter the profesor name')
  
  def __str__(self):
    """String for representing the Model object."""
    return self.name
  
  def get_absolute_url(self):
    return reverse('professor-detail', args=[str(self.id)])

class Level(models.Model):
  """Model representing a level of study."""
  name = models.CharField(max_length=200, help_text='Enter the level of study')

  def __str__(self):
    """String for representing the Model object."""
    return self.name

class Department(models.Model):
  """Model representing a department."""
  name = models.CharField(verbose_name='Department Name', max_length=200, help_text='Enter the department name')
  building_location = models.CharField(verbose_name='Building Location', max_length=200, help_text='Enter the building location', blank=True)
  head_of_department = models.CharField(verbose_name='Head of Department', max_length=200, help_text='Enter the head of department')
  def __str__(self):
    """String for representing the Model object."""
    return self.name

class Course(models.Model):
  """Model representing a course."""
  course_code = models.CharField(verbose_name='Course Code', max_length=200, help_text='Enter the course code')
  title = models.CharField(verbose_name='Course Title', max_length=200, help_text='Enter the course title')
  description = models.TextField(verbose_name='Course Description', help_text='Enter the course description', blank=True)
  academic_level = models.ForeignKey('Level', on_delete=models.SET_NULL, null=True)
  department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
  topic = models.CharField(verbose_name='Course Topic', max_length=255, help_text='Enter the course topic', blank=True)
  visit_count = models.PositiveIntegerField(default=0)

  def __str__(self):
    """String for representing the Model object."""
    return self.title
  
  def get_absolute_url(self):
    """Returns the url to access a detail record for this course."""
    return reverse('course-detail', args=[str(self.id)])
  
class Student(models.Model):
  """Model representing a student."""
  user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
  first_name = models.CharField(verbose_name='First Name', max_length=200, help_text='Enter the student first name')
  last_name = models.CharField(verbose_name='Last Name', max_length=200, help_text='Enter the student last name')
  student_id = models.CharField(verbose_name='Student ID', max_length=50, unique=True, help_text='Enter the student ID')
  enrollment_year = models.IntegerField(verbose_name='Enrollment Year', blank=True, null=True, help_text='Enter the enrollment year')
  
  def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
  
  def get_absolute_url(self):
    return reverse('student-detail', args=[str(self.id)])

class ClassGroup(models.Model):
  # Defining placeholder choices for ENROLLMENT_STATUS
  ENROLLMENT_STATUS_CHOICES = [
      ('OPEN', 'Open'),
      ('CLOSED', 'Closed'),
  ]

  class_id = models.CharField(verbose_name='Class Group ID', max_length=50, unique=True, help_text='Enter the class group ID')
  start_date = models.DateField(verbose_name='Start Date', blank=True, null=True)
  end_date = models.DateField(verbose_name='End Date', blank=True, null=True)
  status = models.CharField(verbose_name='Enrollment Status', max_length=20, choices=ENROLLMENT_STATUS_CHOICES, default='OPEN')
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='class_groups')
  schedule = models.CharField(verbose_name='Class Schedule', max_length=255, blank=True, help_text='Enter the class schedule (e.g., Mon/Wed/Fri 10:00-11:00)')
  maxStudents = models.IntegerField(verbose_name='Maximum Students', help_text='Enter the maximum number of students')
  profesor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, related_name='classes')
  
  # ManyToMany handles the 0..* to 0..* relationship between Students and ClassGroups
  enrolled_students = models.ManyToManyField(Student, related_name='classes', blank=True)

  def __str__(self):
      return f"Class {self.class_id} for {self.course.title}"
  
  @property
  def computed_status(self):
      """
      Returns FULL automatically if the class reached its capacity.
      Otherwise returns the manual one.
      """
      if self.status == 'OPEN':
        
        if self.enrolled_students.count() >= self.maxStudents:
            return 'FULL'
        
        return 'OPEN'

      return self.status