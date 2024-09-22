from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EmployeeViewSet, TaskViewSet

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet)
router.register(r"tasks", TaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
