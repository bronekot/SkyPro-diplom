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
        serializer = self.get_serializer(employees, many=True)
        return Response(serializer.data)


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
        """
        Получить список важных задач с рекомендуемыми исполнителями.

        Важными считаются задачи, которые еще не начаты, но имеют активные подзадачи.
        Для каждой важной задачи предлагается исполнитель на основе текущей загруженности сотрудников.

        Returns:
            Response: Список важных задач с рекомендуемыми исполнителями.
        """
        important_tasks = Task.objects.filter(status="not_started", subtasks__status="in_progress").distinct()

        result = []
        for task in important_tasks:
            least_busy_employee = (
                Employee.objects.annotate(
                    active_tasks_count=Count("tasks", filter=Q(tasks__status__in=["not_started", "in_progress"]))
                )
                .order_by("active_tasks_count")
                .first()
            )

            parent_task_assignee = task.parent_task.assignee if task.parent_task else None
            if parent_task_assignee:
                parent_assignee_tasks = parent_task_assignee.tasks.filter(
                    status__in=["not_started", "in_progress"]
                ).count()
                if parent_assignee_tasks <= least_busy_employee.active_tasks_count + 2:
                    suggested_employee = parent_task_assignee
                else:
                    suggested_employee = least_busy_employee
            else:
                suggested_employee = least_busy_employee

            result.append(
                {
                    "task": TaskSerializer(task).data,
                    "suggested_employee": EmployeeSerializer(suggested_employee).data,
                }
            )

        return Response(result)
