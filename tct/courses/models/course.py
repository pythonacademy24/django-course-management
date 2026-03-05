from django.db import models

from tct.student.views import Student
from tct.teacher.models import Teacher


class Course(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("dropped", "Dropped"),
        ("draft", "Draft"),
    ]
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
        through="Enrollment",
        related_name="courses",
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )
