from django.db import models


class Teacher(models.Model):

    teacher = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

