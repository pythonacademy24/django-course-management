from rest_framework import serializers
from tct.teacher.models import Teacher


class TeacherSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    teacher = serializers.CharField()
    email = serializers.EmailField()


class TeacherCreateSerializer(serializers.Serializer):
    teacher = serializers.CharField()
    email = serializers.EmailField()

    def create(self, validated_data):
        return Teacher.objects.create(**validated_data)


class TeacherUpdateSerializer(serializers.Serializer):
    teacher = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(max_length=100, required=False)

    def update(self, instance, validated_data):
        instance.teacher = validated_data.get("teacher", instance.teacher)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance
