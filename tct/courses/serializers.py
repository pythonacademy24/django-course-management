from rest_framework import serializers
from tct.courses.models import Course
from tct.teacher.models import Teacher
from tct.teacher.serializers import TeacherSerializer
from tct.student.serializers import StudentSerializer


class CourseReadSerializer(serializers.Serializer):
   id = serializers.IntegerField(read_only=True)
   name = serializers.CharField(max_length=100)
   teacher = TeacherSerializer()
   starting_date = serializers.DateField()
   ending_date = serializers.DateField()
   number_of_students = serializers.IntegerField()
   student = StudentSerializer(many=True)


class CourseCreateSerializer(serializers.Serializer):
   name = serializers.CharField(max_length=100)
   teacher_id = serializers.IntegerField()
   starting_date = serializers.DateField()
   ending_date = serializers.DateField()
   number_of_students = serializers.IntegerField()



   def validate_number_of_students(self, value):
       if value < 0:
           raise serializers.ValidationError("Number of students cannot be negative.")
       return value


   def validate(self, data):
       if data.get("starting_date") > data.get("ending_date"):
           raise serializers.ValidationError(
               "Starting date must be before ending date."
           )
       return data


class CourseUpdateSerializer(serializers.Serializer):
   name = serializers.CharField(max_length=100, required=False)
   teacher = serializers.CharField(max_length=100, required=False)
   starting_date = serializers.DateField(required=False)
   ending_date = serializers.DateField(required=False)
   number_of_students = serializers.IntegerField(required=False)

   def validate_number_of_students(self, value):
       if value < 0:
           raise serializers.ValidationError("Number of students cannot be negative.")
       return value

   def validate(self, data):
       if (data.get("starting_date") and data.get("ending_date")
               and data.get("starting_date") > data.get("ending_date")):
           raise serializers.ValidationError(
               "Starting date must be before ending date."
           )
       return data

   def update(self, instance, validated_data):
       instance.name = validated_data.get("name", instance.name)
       instance.teacher = validated_data.get("teacher", instance.teacher)
       instance.starting_date = validated_data.get("starting_date", instance.starting_date)
       instance.ending_date = validated_data.get("ending_date", instance.ending_date)
       instance.number_of_students = validated_data.get(
           "number_of_students", instance.number_of_students
       )
       instance.save()
       return instance