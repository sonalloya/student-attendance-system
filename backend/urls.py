from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, AttendanceViewSet, user_role, my_attendance, teacher_mark_attendance

router = DefaultRouter()
router.register('students', StudentViewSet)
router.register('attendance', AttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user/role/', user_role, name='user-role'),
    path('my-attendance/', my_attendance, name='my-attendance'),
    path('mark-attendance/', teacher_mark_attendance, name='mark-attendance'),
]
