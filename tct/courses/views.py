from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.shortcuts import get_object_or_404

from tct.courses.data_service.course import CourseService
from tct.courses.data_service.enrollment import EnrollmentService
from tct.courses.models.course import Course
from tct.courses.serializers import EnrollmentSerializer
from tct.courses.serializers.course import CourseReadSerializer, CourseUpdateSerializer, CourseCreateSerializer
from tct.pagination import TCTPagination
from tct.utils import enroll_student, unroll_student


class CourseListView(APIView):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseReadSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseListFilteredView(APIView):
    # check if is authenticated
    def get(self, request):
        courses = Course.objects.all()

        teacher = request.query_params.get("teacher")
        print(teacher, 'TEACHER VALUE')
        if teacher:
            courses = courses.filter(teacher__teacher__icontains=teacher)
            # same as below
            # courses = Course.objects.filter(teacher=teacher)
        number_of_std = request.query_params.get("number_of_students")
        if number_of_std:
            courses = courses.filter(number_of_students__gte=number_of_std)
            # same as below
            # courses = Course.objects.filter(
            # number_of_students__gte=number_of_std
            # )

        name = request.query_params.get("name")
        if name:
            courses = courses.filter(name__icontains=name)
            # same as below
            # courses = Course.objects.filter(name=name)

        paginator = TCTPagination()
        paginated_courses = paginator.paginate_queryset(courses, request)
        serializer = CourseReadSerializer(paginated_courses, many=True)
        return paginator.get_paginated_response(serializer.data)


class CourseCreateView(APIView):

    def post(self, request):
        serializer = CourseCreateSerializer(data=request.data)

        if serializer.is_valid():
            course = CourseService().create_course(
                serializer.validated_data
            )

            return Response(
                CourseCreateSerializer(course).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CourseUpdateDeleteView(APIView):

    def put(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseUpdateSerializer(course, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseUpdateSerializer(
            course,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        if course.number_of_students > 0:
            return Response(
                {
                    "error": "Cannot delete a course with enrolled students."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        course.delete()
        return Response(
            {"message": "Course deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


class CourseEnrollView(APIView):
    def patch(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        student_ids = request.data.get("student_ids")

        if not student_ids or not isinstance(student_ids, list):
            return Response(
                {"error": "Student is required or must be a list !!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrolled_students = enroll_student(
            course=course,
            student_ids=student_ids
        )
        return Response(
            {
                "message": "Successfully enrolled students!!",
                "enrolled_students": enrolled_students
            },
            status=status.HTTP_200_OK
        )


class CourseUnrollView(APIView):
    def patch(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        student_ids = request.data.get("student_ids")

        if not student_ids or not isinstance(student_ids, list):
            return Response(
                {"error": "Student is required or must be a list !!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrolled_students = unroll_student(
            course=course,
            student_ids=student_ids
        )
        return Response(
            {
                "message": "Successfully unrolled students!!",
                "enrolled_students": enrolled_students
            },
            status=status.HTTP_200_OK
        )


class CourseBulkImportView(APIView):

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "File is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        service = CourseService()
        report = service.import_courses(file)
        errors = report["errors"]
        if errors:
            error_file = service.generate_error_file(
                errors
            )
            response = HttpResponse(
                error_file,
                content_type="text/csv"
            )
            response["Content-Disposition"] = (
                "attachment; filename=import_errors.csv"
            )
            return response
        return Response(report)


class EnrollStudentView(APIView):
    def post(self, request):
        serializer = EnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            _ = EnrollmentService().enroll_student(
                serializer.validated_data["student_id"],
                serializer.validated_data["course_id"]
            )
            return Response(
                {
                    "message": "Student enrolled successfully!!"
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DropStudentView(APIView):
    def post(self, request):
        serializer = EnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            _ = EnrollmentService().drop_student(
                serializer.validated_data["student_id"],
                serializer.validated_data["course_id"]
            )
            return Response(
                {
                    "message": "Student dropped successfully!!"
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseProgressView(APIView):
    def get(self, request, course_id):
        progress = CourseService().get_course_progress(course_id)
        return Response(
            {
                "course_id": course_id,
                "progress": progress
            }
        )
