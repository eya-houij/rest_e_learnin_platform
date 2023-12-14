from datetime import timezone
from django import forms
from authentication_app.models import Assignment, Course, Material, ReadingState



class ReadingStateForm(forms.ModelForm):
    class Meta:
        model = ReadingState
        fields = ['material', 'read_state']
class CourseRegistrationForm(forms.Form):
    course_name = forms.CharField(max_length=255, required=True)
    material_title = forms.CharField(max_length=255, required=True)

    def clean_material_title(self):
        material_title = self.cleaned_data['material_title']
        # Check if the material with the specified title exists
        if not Material.objects.filter(title=material_title).exists():
            raise forms.ValidationError(f"Material with title '{material_title}' does not exist.")
        return material_title

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        course_name = forms.CharField(max_length=255, required=True)
        submission_file = forms.FileField(required=True)
    def clean(self):
        cleaned_data = super().clean()
        submission_file = cleaned_data.get('submission_file')

        # Assuming you have a field 'deadline' in your Assignment model
        assignment = self.instance.assignment  # Assuming AssignmentSubmission has a foreign key to Assignment
        if assignment.deadline and timezone.now() > assignment.deadline:
            raise forms.ValidationError("Submission deadline has passed. Submission is not allowed.")

        return cleaned_data