from django.contrib import admin
from authentication_app.models import Course
from authentication_app.models import Material
from authentication_app.models import Assignment
from authentication_app.models import Submission
from authentication_app.models import Grade

admin.site.register(Course)
admin.site.register(Material)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Grade)