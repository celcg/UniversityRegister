from django.db import models

# Create your models here.
class Professor(models.Model):
  """Model representing a professor."""
  name = models.CharField(max_length=200, help_text='Enter the professor name')

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
  professor = models.ForeignKey('Professor', on_delete=models.SET_NULL, null=True)

  def __str__(self):
    """String for representing the Model object."""
    return self.title
