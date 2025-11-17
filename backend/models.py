from django.db import models
from datetime import date
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile',null=True, blank=True)
    # name = models.CharField(max_length=100)
    rollno = models.CharField(max_length=20)
    student_class = models.CharField(max_length=20)

    class Meta:
        unique_together = ('rollno', 'student_class')

    def __str__(self):
        username = self.user.username if self.user else "UnlinkedUser"
        return f"{username} ({self.rollno} - {self.student_class})"


class Attendance(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    status = models.BooleanField(default=False) 

    def __str__(self):
        student_name = self.student.user.username if (self.student and self.student.user) else "unknown Student"
        return f"{student_name} - {self.date} - {'Present' if self.status else 'Absent'}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile',null=True, blank=True)
    assigned_class = models.CharField(max_length=20)

    def __str__(self):
        username = self.user.username if self.user else "UnlinkedTeacher"
        return f"{username} - {self.assigned_class}"
