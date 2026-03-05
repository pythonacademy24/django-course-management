from abc import ABC

from tct.courses.models import Enrollment
from tct.courses.models.course import Course
from tct.student.models import Student
from django.core.exceptions import ValidationError


class AbstractEnrollmentService(ABC):

    @staticmethod
    def enroll_student(course_id, student_id):
        raise NotImplementedError

    @staticmethod
    def drop_student(course_id, student_id):
        raise NotImplementedError


class EnrollmentService(AbstractEnrollmentService):

    @staticmethod
    def enroll_student(course_id, student_id):
        student = Student.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)

        if course.status != "active":
            raise ValidationError("Can not enroll in inactive course!!")
        if course.student.count() >= course.number_of_students:
            raise ValidationError("Course capacity reached!!")

        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            course=course
        )
        return enrollment

    @staticmethod
    def drop_student(course_id, student_id):
        enrollment = Enrollment.objects.get(
            student_id=student_id,
            course_id=course_id
        )
        if not enrollment:
            raise ValidationError("Student not enrolled to this course!!")
        enrollment.status = "dropped"
        enrollment.save()
        return enrollment
