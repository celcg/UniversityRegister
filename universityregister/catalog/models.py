from django.db import models

class Profesor(models.Model):
  """Model representing a profesor."""
  name = models.CharField(max_length=200, help_text='Enter the profesor name')
  def __str__(self):
    """String for representing the Model object."""
    return self.name

class Level(models.Model):
  """Model representing a level of study."""
  name = models.CharField(max_length=200, help_text='Enter the level of study')

  def __str__(self):
    """String for representing the Model object."""
    return self.name

class Department(models.Model):
  """Model representing a department."""
  name = models.CharField(max_length=200, help_text='Enter the department name')
  building_location = models.CharField(max_length=200, help_text='Enter the building location')
  head_of_department = models.CharField(max_length=200, help_text='Enter the head of department')
  def __str__(self):
    """String for representing the Model object."""
    return self.name

class Course(models.Model):
  """Model representing a course."""
  course_code = models.CharField(max_length=200, help_text='Enter the course code')
  title = models.CharField(max_length=200, help_text='Enter the course title')
  description = models.TextField(help_text='Enter the course description')
  academic_level = models.ForeignKey('Level', on_delete=models.SET_NULL, null=True)
  department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
  topic = models.CharField(max_length=255, help_text='Enter the course topic')
  #profesor = models.ForeignKey('Profesor', on_delete=models.SET_NULL, null=True)

  def __str__(self):
    """String for representing the Model object."""
    return self.title
  
class Student(models.Model):
  """Model representing a student."""
  first_name = models.CharField(max_length=200, help_text='Enter the student first name')
  last_name = models.CharField(max_length=200, help_text='Enter the student last name')
  student_id = models.CharField(max_length=50, unique=True, help_text='Enter the student ID')
  enrollment_year = models.IntegerField()
  def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"
class ClassGroup(models.Model):
  # Defining placeholder choices for ENROLLMENT_STATUS
  ENROLLMENT_STATUS_CHOICES = [
      ('OPEN', 'Open'),
      ('CLOSED', 'Closed'),
      ('FULL', 'Full'),
  ]

  class_id = models.CharField(max_length=50, unique=True)
  start_date = models.DateField()
  end_date = models.DateField()
  status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS_CHOICES, default='OPEN')
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='class_groups')
  schedule = models.CharField(max_length=255)
  maxStudents = models.IntegerField()
  profesor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, related_name='classes')
  
  # ManyToMany handles the 0..* to 0..* relationship between Students and ClassGroups
  enrolled_students = models.ManyToManyField(Student, related_name='classes', blank=True)

  def __str__(self):
      return f"Class {self.class_id}, date {self.start_date} for {self.course.title}"