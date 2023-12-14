from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group


validate_alphanumeric = RegexValidator(
    r'^[a-zA-Z0-9]*$',
    'Only alphanumeric characters are allowed.'
)

class RoleEnum(models.TextChoices):
    ADMINISTRATOR = 'ADMINISTRATOR', 'Administrator'
    TUTOR = 'TUTOR', 'Tutor'
    STUDENT = 'STUDENT', 'Student'

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not role:
            raise ValueError('Users must have a role')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            role=role,
        )
        user.set_password(password)
        user.is_active=True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            email=email,
            username=username,
            role=RoleEnum.ADMINISTRATOR,
        )
        user.set_password(password)
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateField(auto_now_add=True)
    role = models.CharField(max_length=200, choices=RoleEnum.choices, default=RoleEnum.STUDENT)
    last_login = models.DateTimeField(null=True, blank=True)
    password =  models.CharField(max_length=200)
    email_confirmed = models.CharField(max_length=200, default=True)
    groups = models.ManyToManyField(Group, blank=True, related_name='users')

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role']

    class Meta:
        db_table = 'Users'

    def __str__(self):
        return self.username

class RevokedToken(models.Model):
    token = models.CharField(max_length=800)
    def __str__(self):
        return self.token 
    
class Course(models.Model):
    courseId = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    enrollmentCapacity = models.IntegerField()
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class Material(models.Model):
    materialId = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    uploadDate = models.DateField(auto_now_add=True)
    documentType = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

class Assignment(models.Model):
    assignmentId = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    dueDate = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

class Submission(models.Model):
    submissionId = models.AutoField(primary_key=True)
    submissionContent = models.TextField()
    submissionDate = models.DateField(auto_now_add=True)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

class Grade(models.Model):
    gradeId = models.AutoField(primary_key=True)
    grade = models.CharField(max_length=10)
    feedback = models.TextField()
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

class ReportedIncident(models.Model):
    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reported_user = models.ForeignKey(CustomUser, related_name='reported_user', on_delete=models.CASCADE)
    description = models.TextField()
    resolved = models.BooleanField(default=False)