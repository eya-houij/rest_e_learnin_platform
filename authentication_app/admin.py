from django.contrib import admin
from .models import CustomUser, RevokedToken

admin.site.register(CustomUser)
admin.site.register(RevokedToken)