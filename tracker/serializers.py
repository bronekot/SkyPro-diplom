from django.utils import timezone
from rest_framework import serializers

from .models import Employee, Task


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "full_name", "position"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "name", "parent_task", "assignee", "deadline", "status", "created_at"]

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Срок выполнения не может быть в прошлом.")
        return value

    def validate(self, data):
        if "id" in self.initial_data and data.get("parent_task") and self.initial_data["id"] == data["parent_task"].id:
            raise serializers.ValidationError("Задача не может быть своим собственным родителем.")
        return data
