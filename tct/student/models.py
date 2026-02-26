from django.db import models


class Student(models.Model):
    student = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
