import random
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с сотрудниками.

    Поддерживает операции создания, чтения, обновления и удаления (CRUD) для сотрудников.
    """

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    @extend_schema(
        description="Получить список сотрудников, отсортированный по количеству активных задач.",
        responses={200: EmployeeSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def busy_employees(self, request):
        """
        Получить список сотрудников, отсортированный по количеству активных задач.

        Returns:
            Response: Список сотрудников с количеством их активных задач.
        """
        employees = Employee.objects.annotate(
            active_tasks_count=Count("tasks", filter=Q(tasks__status__in=["not_started", "in_progress"]))
        ).order_by("-active_tasks_count")
        result = []
        for employee in employees:
            result.append(
                {
                    "ФИО": employee.full_name,
                    "ID": employee.id,
                    "Должность": employee.position,
                    "Количество активных задач": employee.active_tasks_count,
                }
            )
        return Response(result)


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с задачами.

    Поддерживает операции создания, чтения, обновления и удаления (CRUD) для задач.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @extend_schema(
        description="Получить список важных задач с рекомендуемыми исполнителями.",
        responses={200: TaskSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def important_tasks(self, request):
        important_tasks = Task.objects.filter(
            Q(status="not_started", subtasks__status="in_progress")
            | Q(assignee__isnull=True, subtasks__status="in_progress")
        ).distinct()

        result = []
        for task in important_tasks:
            suggested_employee = None
            suggested_reason = ""

            employees = Employee.objects.annotate(
                active_tasks_count=Count("tasks", filter=Q(tasks__status__in=["not_started", "in_progress"]))
            ).order_by("active_tasks_count")

            if not task.assignee:
                if employees.exists():
                    least_busy_employee = employees.first()
                    min_tasks = least_busy_employee.active_tasks_count
                    subtask_assignee = task.subtasks.filter(status="in_progress").values("assignee").first()
                    if subtask_assignee:
                        subtask_employee = employees.get(id=subtask_assignee["assignee"])

                        if subtask_employee.active_tasks_count <= min_tasks + 2:
                            suggested_employee = subtask_employee
                            suggested_reason = "Сотрудник подзадачи не сильно загружен"
                        else:
                            suggested_employee = random.choice(employees.filter(active_tasks_count=min_tasks))
                            suggested_reason = "Случайный наименее загруженный сотрудник"
                    else:
                        suggested_employee = random.choice(employees.filter(active_tasks_count=min_tasks))
                        suggested_reason = "Случайный наименее загруженный сотрудник"
            else:
                suggested_employee = employees.get(id=task.assignee.id)
                suggested_reason = "Уже назначенный исполнитель"

            active_tasks_count = suggested_employee.active_tasks_count if suggested_employee else None

            result.append(
                {
                    "Важная задача": task.name,
                    "ID задачи": task.id,
                    "Срок": task.deadline.strftime("%Y-%m-%d") if task.deadline else None,
                    "ФИО предлагаемого сотрудника": suggested_employee.full_name if suggested_employee else [],
                    "ID предлагаемого сотрудника": suggested_employee.id if suggested_employee else None,
                    "Причина предложения": suggested_reason,
                    "Количество активных задач": active_tasks_count,
                }
            )

        return Response(result)
