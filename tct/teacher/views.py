from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from tct.teacher.data_service import TeacherDataService
from tct.teacher.serializers import TeacherSerializer, TeacherCreateSerializer, TeacherUpdateSerializer
from tct.pagination import TCTPagination
from tct.teacher.models import Teacher


class TeacherListView(APIView):
   def get(self, request, pk):
       teacher = get_object_or_404(Teacher, pk=pk)
       serializer = TeacherSerializer(teacher)
       return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherListFilteredView(APIView):
   def get(self, request):
       teacher_data = Teacher.objects.all()

       teacher_name = request.query_params.get("teacher")
       if teacher_name:
           teacher_data = teacher_data.filter(teacher__icontains=teacher_name)
           # same as below
           # teacher = Teacher.objects.filter(teacher=teacher)
       email = request.query_params.get("email")
       if email:
           teacher_data = teacher_data.filter(email=email)
           # same as below
           # teacher = Teacher.objects.filter(
           # email=email
           # )

       paginator = TCTPagination()
       paginated_teachers = paginator.paginate_queryset(teacher_data, request)
       serializer = TeacherSerializer(paginated_teachers, many=True)
       return paginator.get_paginated_response(serializer.data)


class TeacherCreateView(APIView):

   def post(self, request):
       serializer = TeacherCreateSerializer(data=request.data)


       if serializer.is_valid():
           serializer.save()
           return Response(
               serializer.data,
               status=status.HTTP_201_CREATED
           )
       return Response(
           serializer.errors,
           status=status.HTTP_400_BAD_REQUEST
       )


class TeacherUpdateDeleteView(APIView):

   def put(self, request, pk):
       teacher = get_object_or_404(Teacher, pk=pk)
       serializer = TeacherUpdateSerializer(teacher, data=request.data)

       if serializer.is_valid():
           serializer.save()
           return Response(serializer.data, status=status.HTTP_200_OK)

       return Response(
           serializer.errors,
           status=status.HTTP_400_BAD_REQUEST
       )

   def patch(self, request, pk):
       teacher = get_object_or_404(Teacher, pk=pk)
       serializer = TeacherUpdateSerializer(
           teacher,
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
       teacher = get_object_or_404(Teacher, pk=pk)
       if teacher.courses.exists():
           return Response(
               {
                   "error": "Cannot delete a teacher with an active course."
               },
               status=status.HTTP_400_BAD_REQUEST
           )

       teacher.delete()
       return Response(
           {"message": "Teacher deleted successfully"},
           status=status.HTTP_204_NO_CONTENT
           )


class TeacherBulkCreateView(APIView):

    def post(self, request):
        file = request.FILE.get("file")

        if not file:
            return Response(
                {
                    "error": "File is required!!"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        service = TeacherDataService()
        report = service.import_teachers(file)
        return Response(
            report,
            status=status.HTTP_201_CREATED
        )
