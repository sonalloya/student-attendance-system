from django.contrib import admin
from .models import Student, Attendance, Teacher

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'rollno', 'student_class')
    search_fields = ('user', 'rollno', 'student_class')
    list_filter = ('student_class',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    search_fields = ('student__name', 'student__rollno')
    list_filter = ('date', 'status','student__student_class')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'assigned_class')
    search_fields = ('user__username', 'assigned_class')

