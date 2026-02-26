from rest_framework import serializers
from tct.student.models import Student


class StudentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    student = serializers.CharField()
    email = serializers.EmailField()


class StudentCreateSerializer(serializers.Serializer):
    student = serializers.CharField()
    email = serializers.EmailField()

    def create(self, validated_data):
        return Student.objects.create(**validated_data)


class StudentUpdateSerializer(serializers.Serializer):
    student = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(max_length=100, required=False)

    def update(self, instance, validated_data):
        instance.student = validated_data.get("student", instance.student)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance

