from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer


class EmployeeModelTest(TestCase):
    def test_create_employee(self):
        employee = Employee.objects.create(full_name="Иван Иванов", position="Разработчик")
        self.assertEqual(employee.full_name, "Иван Иванов")
        self.assertEqual(employee.position, "Разработчик")

    def test_employee_str_method(self):
        employee = Employee.objects.create(full_name="Петр Петров", position="Менеджер")
        self.assertEqual(str(employee), "Петр Петров")


class TaskModelTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(full_name="Мария Петрова", position="Менеджер")

    def test_create_task(self):
        task = Task.objects.create(
            name="Тестовая задача",
            assignee=self.employee,
            deadline=timezone.now() + timedelta(days=1),
            status="not_started",
        )
        self.assertEqual(task.name, "Тестовая задача")
        self.assertEqual(task.assignee, self.employee)
        self.assertEqual(task.status, "not_started")

    def test_task_activity(self):
        task = Task.objects.create(
            name="Активная задача",
            assignee=self.employee,
            deadline=timezone.now() + timedelta(days=1),
            status="in_progress",
        )
        self.assertTrue(task.is_active())

        task.status = "completed"
        task.save()
        self.assertFalse(task.is_active())

    def test_task_str_method(self):
        task = Task.objects.create(
            name="Задача для теста",
            assignee=self.employee,
            deadline=timezone.now() + timedelta(days=1),
            status="not_started",
        )
        self.assertEqual(str(task), "Задача для теста")

    def test_task_validation(self):
        with self.assertRaises(ValidationError):
            Task.objects.create(
                name="Неверная задача",
                assignee=self.employee,
                deadline=timezone.now() - timedelta(days=1),
                status="not_started",
            )


class EmployeeSerializerTest(TestCase):
    def test_employee_serializer(self):
        employee_data = {"full_name": "Анна Сидорова", "position": "Дизайнер"}
        serializer = EmployeeSerializer(data=employee_data)
        self.assertTrue(serializer.is_valid())
        employee = serializer.save()
        self.assertEqual(employee.full_name, "Анна Сидорова")
        self.assertEqual(employee.position, "Дизайнер")


class TaskSerializerTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(full_name="Олег Николаев", position="Разработчик")

    def test_task_serializer(self):
        task_data = {
            "name": "Тестовая задача",
            "assignee": self.employee.id,
            "deadline": (timezone.now() + timedelta(days=1)).isoformat(),
            "status": "not_started",
        }
        serializer = TaskSerializer(data=task_data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.name, "Тестовая задача")
        self.assertEqual(task.assignee, self.employee)

    def test_task_serializer_invalid_deadline(self):
        task_data = {
            "name": "Задача с прошедшим сроком",
            "assignee": self.employee.id,
            "deadline": (timezone.now() - timedelta(days=1)).isoformat(),
            "status": "not_started",
        }
        serializer = TaskSerializer(data=task_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("deadline", serializer.errors)


class EmployeeAPITest(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(full_name="Алексей Сидоров", position="Дизайнер")

    def test_employee_list(self):
        response = self.client.get("/api/employees/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_employee(self):
        data = {"full_name": "Петр Петров", "position": "Тестировщик"}
        response = self.client.post("/api/employees/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 2)

    def test_update_employee(self):
        data = {"full_name": "Алексей Сидоров", "position": "Старший дизайнер"}
        response = self.client.put(f"/api/employees/{self.employee.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.position, "Старший дизайнер")

    def test_delete_employee(self):
        response = self.client.delete(f"/api/employees/{self.employee.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.count(), 0)


class TaskAPITest(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(full_name="Ольга Кузнецова", position="Проект-менеджер")
        self.task = Task.objects.create(
            name="API Задача",
            assignee=self.employee,
            deadline=timezone.now() + timedelta(days=1),
            status="not_started",
        )

    def test_task_list(self):
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_task(self):
        data = {
            "name": "Новая API задача",
            "assignee": self.employee.id,
            "deadline": (timezone.now() + timedelta(days=2)).isoformat(),
            "status": "not_started",
        }
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_update_task(self):
        data = {
            "name": "Обновленная API задача",
            "assignee": self.employee.id,
            "deadline": (timezone.now() + timedelta(days=3)).isoformat(),
            "status": "in_progress",
        }
        response = self.client.put(f"/api/tasks/{self.task.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Обновленная API задача")
        self.assertEqual(self.task.status, "in_progress")

    def test_delete_task(self):
        response = self.client.delete(f"/api/tasks/{self.task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_busy_employees_endpoint(self):
        response = self.client.get("/api/employees/busy_employees/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_important_tasks_endpoint(self):
        response = self.client.get("/api/tasks/important_tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_important_tasks_with_subtasks(self):
        parent_task = Task.objects.create(
            name="Родительская задача",
            assignee=self.employee,
            deadline=timezone.now() + timedelta(days=5),
            status="not_started",  # Изменено с "in_progress" на "not_started"
        )
        _ = Task.objects.create(
            name="Подзадача",
            assignee=self.employee,
            deadline=timezone.now() + timedelta(days=3),
            status="in_progress",  # Изменено с "not_started" на "in_progress"
            parent_task=parent_task,
        )
        response = self.client.get("/api/tasks/important_tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Выводим содержимое ответа для отладки
        print("Response data:", response.data)

        # Проверяем, есть ли родительская задача в списке важных задач
        found = any(task["task"]["id"] == parent_task.id for task in response.data)
        if not found:
            print(f"Parent task with id {parent_task.id} not found in important tasks")
            # Выводим ID всех задач в ответе
            task_ids = [task["task"]["id"] for task in response.data]
            print("Task IDs in response:", task_ids)

        self.assertTrue(found, "Родительская задача не найдена в списке важных задач")
