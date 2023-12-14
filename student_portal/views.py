from django.shortcuts import render, redirect
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from authentication_app import views
from authentication_app.models import Course, Material, Assignment, ReadingState
from student_portal import forms
from student_portal.froms import AssignmentSubmissionForm, ReadingStateForm
from .serializers import CourseSerializer, MaterialSerializer, AssignmentSerializer, ReadingStateSerializer

class SaveDocumentStateView(views):
    template_name = 'ReadingState.html'
    def get(self, request):
        form = ReadingStateForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ReadingStateForm(request.POST)
        if form.is_valid():
            # Assuming you have a user, student, and document objects
            user = request.user
            student = user.student  # Update this according to your user and student logic
            document = ...  # Get the document based on your logic

            if student and document:
                # Update or create the document state
                Reading_state, created = ReadingState.objects.update_or_create(
                    student=student,
                    document=document,
                    defaults={'read_state': form.cleaned_data['read_state']}
                )

                return render(request, 'success.html', {'Reading_state': Reading_state})

        return render(request, self.template_name, {'form': form})
    
class AssignmentSubmissionView(views):
    permission_classes = [permissions.IsAuthenticated, permissions.Can view assignment]
    template_name = 'assignment_submission.html'

    def get(self, request, assignment_id):
        form = AssignmentSubmissionForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, assignment_id):
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            # Assuming you have a user and assignment objects
            user = request.user
            assignment = ...  # Get the assignment based on your logic

            if assignment:
                # Update or create the assignment submission
                assignment.submission = form.cleaned_data['submission']
                assignment.save()

                return render(request, 'assignment_submission_success.html', {'assignment': assignment})

        return render(request, self.template_name, {'form': form})

class EnrollCourseView(generics.CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        student = request.user.student  # Assuming you have a user model with a OneToOneField to Student

        try:
            course = Course.objects.get(id=course_id, enrollment_capacity__gt=0)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found or enrollment capacity is full.'}, status=status.HTTP_400_BAD_REQUEST)

        if student.courses.filter(id=course_id).exists():
            return Response({'error': 'Student is already enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)

        student.courses.add(course)
        course.enrollment_capacity -= 1
        course.save()

        return Response({'message': 'Enrollment successful.'}, status=status.HTTP_201_CREATED)

class AccessMaterialView(generics.RetrieveAPIView):
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        course_id = self.kwargs.get('course_id')
        material_id = self.kwargs.get('material_id')

        try:
            course = Course.objects.get(id=course_id, enrollment_capacity__gt=0)
            material = Material.objects.get(id=material_id, course=course)
        except (Course.DoesNotExist, Material.DoesNotExist):
            return None

        return material

class SubmitAssignmentView(generics.CreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        assignment_data = request.data
        assignment_data['student'] = request.user.student.id
        serializer = self.get_serializer(data=assignment_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Assignment submitted successfully.'}, status=status.HTTP_201_CREATED)

class ViewGradesView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        student = self.request.user.student
        return Assignment.objects.filter(student=student)

class ReadingStateView(generics.UpdateAPIView):
    serializer_class = ReadingStateSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        # Retrieve the parameters from the request data or URL parameters
        student_id = self.request.data.get('student_id')  # Replace with the actual parameter name
        document_id = self.request.data.get('document_id')  # Replace with the actual parameter name

        # Implement logic to retrieve the document state based on student and document
        try:
            document_state = ReadingState.objects.get(student_id=student_id, document_id=document_id)
        except ReadingState.DoesNotExist:
            # Handle the case when the document state does not exist
            document_state = None

        return document_state

    def update(self, request, *args, **kwargs):
        # Ensure you have the logic to update the document state based on the request data
        document_state = self.get_object()
        if document_state is not None:
            serializer = self.get_serializer(document_state, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            # Handle the case when the document state does not exist
            return Response({'error': 'Document state not found.'}, status=status.HTTP_404_NOT_FOUND)