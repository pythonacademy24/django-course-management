from django.db import models

from tct.student.views import Student
from tct.teacher.models import Teacher


class Course(models.Model):
   name = models.CharField(max_length=100)
   teacher = models.ForeignKey(
      Teacher,
      on_delete=models.CASCADE,
      related_name="courses"
   )
   starting_date = models.DateField()
   ending_date = models.DateField()
   number_of_students = models.IntegerField()
   student = models.ManyToManyField(
      Student,
      related_name="courses",
      blank=True
   )
