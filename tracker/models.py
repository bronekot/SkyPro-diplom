from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Employee(models.Model):
    full_name = models.CharField(max_length=100, db_index=True)
    position = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name

    class Meta:
        indexes = [
            models.Index(fields=["full_name"]),
        ]


class Task(models.Model):
    STATUS_CHOICES = [
        ("not_started", "Не начата"),
        ("in_progress", "Выполняется"),
        ("completed", "Завершена"),
    ]

    name = models.CharField(max_length=200)
    parent_task = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subtasks")
    assignee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="tasks")
    deadline = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.parent_task == self:
            raise ValidationError("Задача не может быть своим собственным родителем.")
        if self.deadline and self.deadline < timezone.now():
            raise ValidationError("Срок выполнения не может быть в прошлом.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def is_active(self):
        return self.status in ["not_started", "in_progress"]

    class Meta:
        indexes = [
            models.Index(fields=["status", "deadline"]),
            models.Index(fields=["assignee", "status"]),
        ]
