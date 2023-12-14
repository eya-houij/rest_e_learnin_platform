import datetime
from rest_framework import serializers
from django.contrib.auth import authenticate, login
from .models import CustomUser, RoleEnum
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group


class CustomUserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=RoleEnum.choices)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'date_joined', 'role', 'access_token')  # Include 'access_token'

    access_token = serializers.SerializerMethodField() 

    def get_access_token(self, obj):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and obj == request.user:
            refresh = RefreshToken.for_user(obj)
            return str(refresh.access_token)
        return None




class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            try:
                user = CustomUser.objects.get(username=username)
                if user.check_password(password):
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)   #adheya t5alih wa7dou yzid l access_token field
                    data['access_token'] = access_token

                    user.last_login = datetime.datetime.utcnow()
                    user.save(update_fields=['last_login'])

                    data['user'] = user
                else:
                    raise serializers.ValidationError('Unable to authenticate with provided credentials')
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError('User does not exist')
        else:
            raise serializers.ValidationError('Must include "username" and "password"')

        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=RoleEnum.choices)  # Add this line

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'role')

    def create(self, validated_data):
        role_choice = validated_data.pop('role')  # Extract the chosen role
        role = RoleEnum(role_choice)  # Convert the choice to RoleEnum

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role  # Assign the chosen role to the user
        )
        refresh = RefreshToken.for_user(user)
        validated_data['access_token'] = str(refresh.access_token)  # Include access token in responsefrom django.contrib.auth.models import Group

        if role == RoleEnum.STUDENT:
            student_group = Group.objects.get(name='Students')
            user.groups.add(student_group)
        elif role == RoleEnum.TUTOR:
            tutor_group = Group.objects.get(name='Tutors')
            user.groups.add(tutor_group)
        return user
    
class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()