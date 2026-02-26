from rest_framework.exceptions import ValidationError
from django.db import transaction

from tct.student.models import Student


@transaction.atomic
def enroll_student(course, student_ids):
    students_to_enroll = Student.objects.filter(id__in=student_ids)
    enrolled_ids = course.student.values_list("id", flat=True)
    students_to_add = students_to_enroll.exclude(id__in=enrolled_ids)
    if not students_to_add.exists():
        raise ValidationError("All provided students are already enrolled!!")

    course.student.add(*students_to_add)
    course.number_of_students = course.student.count()
    # course.number_of_students += 1
    course.save()
    # return list(students_to_add.values_list("id", flat=True))
    return enrolled_ids


@transaction.atomic
def unroll_student(course, student_ids):
    students_to_unroll = Student.objects.filter(id__in=student_ids)
    enrolled_ids = course.student.values_list("id", flat=True)
    students_to_remove = students_to_unroll.filter(id__in=enrolled_ids)
    if not students_to_remove.exists():
        raise ValidationError("None of these students are enrolled!!")

    course.student.remove(*students_to_remove)
    course.number_of_students = course.student.count()
    # course.number_of_students -= 1
    course.save()
    # return list(students_to_remove.values_list("id", flat=True))
    return enrolled_ids