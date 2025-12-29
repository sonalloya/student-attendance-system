from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from rest_framework import viewsets
from .models import Student, Attendance, Teacher
from .serializers import StudentSerializer, AttendanceSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import  AllowAny
from .permissions import IsTeacher, IsStudent,IsAdmin

@api_view(['GET'])
@permission_classes([AllowAny])
def user_role(request):
    user = request.user
    if user.is_superuser:
        role = 'admin'
    elif hasattr(user, 'teacher_profile'):
        role = 'teacher'
    elif hasattr(user, 'student_profile'):
        role = 'student'
    else:
        role = 'unknown'
    return Response({'username': user.username, 'role': role})

@api_view(['GET'])
@permission_classes([AllowAny])
def my_attendance(request):
    """Student can view their own attendance."""
    if not hasattr(request.user, 'student_profile'):
        return Response({"detail": "You are not a student."}, status=403)

    student = request.user.student_profile
    records = Attendance.objects.filter(student=student).order_by('-date')
    serializer = AttendanceSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def teacher_mark_attendance(request):
    """Teacher can mark attendance for students."""
    if not hasattr(request.user, 'teacher_profile'):
        return Response({"detail": "You are not authorized to mark attendance."}, status=403)

    teacher = request.user.teacher_profile
    data = request.data  # expects list of attendance entries

    for item in data:
        try:
            student = Student.objects.get(id=item['student_id'])
            Attendance.objects.update_or_create(
                student=student,
                date=item['date'],
                defaults={'status': item['status']}
            )
        except Student.DoesNotExist:
            continue  # skip invalid student IDs

    return Response({"detail": "Attendance marked successfully!"})


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def by_class(self, request):
        student_class = request.query_params.get('student_class')
        if not student_class:
        
            return Response({'error': 'student_class required'}, status=status.HTTP_400_BAD_REQUEST)
        students = Student.objects.filter(student_class=student_class)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        student = self.get_object()
        attendance = Attendance.objects.filter(student=student)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
      
    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """Generate a PDF attendance report for this student"""
        student = self.get_object()
        attendance_records = self.get_attendance_records(student)
        pdf_buffer = self.generate_pdf(student, attendance_records)
        return HttpResponse(pdf_buffer, content_type='application/pdf')

    def get_attendance_records(self, student):
        return Attendance.objects.filter(student=student).order_by('date')

    def generate_pdf(self, student, attendance_records):
        # Create PDF in memory
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, height - 50, "Attendance Report")

        # Student info
        p.setFont("Helvetica", 12)
        y = height - 100
        p.drawString(50, y, f"Name: {student.name}")
        p.drawString(50, y - 20, f"Roll No: {student.rollno}")
        p.drawString(50, y - 40, f"Class: {student.student_class}")

        # Table Header
        y -= 80
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Date")
        p.drawString(200, y, "Status")
        p.line(50, y - 5, 550, y - 5)

        # Attendance list
        y -= 25
        p.setFont("Helvetica", 11)
        for record in attendance_records:
            if y < 100:  # new page if too long
                p.showPage()
                y = height - 100
            p.drawString(50, y, str(record.date))
            p.drawString(200, y, "Present" if record.status else "Absent")
            y -= 20

        p.showPage()
        p.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{student.rollno}_attendance_report.pdf"'
        return response


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [AllowAny]
    # permission_class = [IsAuthenticated]
