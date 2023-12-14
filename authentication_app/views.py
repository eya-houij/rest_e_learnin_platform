from django.shortcuts import redirect, render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from authentication_app.forms import UserLoginForm, UserRegistrationForm
from rest_framework.permissions import IsAuthenticated

from .models import RevokedToken, RoleEnum
from .serializers import (
    UserLoginSerializer,
    UserRegistrationSerializer
)





class UserLoginView(APIView):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Validate with the serializer
            serializer = UserLoginSerializer(data={'username': username, 'password': password})
            if serializer.is_valid():
                user = serializer.validated_data['user']
                refresh = RefreshToken.for_user(user)
                token_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }

                if user.role == RoleEnum.TUTOR:
                    return redirect('course-list')  # Redirect to 'course-list' URL name

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return render(request, 'login.html', {'form': form})


class UserRegistrationView(APIView):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'registration.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Validate with the serializer
            serializer = UserRegistrationSerializer(data=form.cleaned_data)
            if serializer.is_valid():
                user=serializer.save()
                # Perform additional actions after successful registration
                refresh = RefreshToken.for_user(user)
                token_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                return Response(
                    {'user': serializer.data, 'tokens': token_data},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return render(request, 'registration.html', {'form': form})
    
    from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        token = request.data.get('token')

        if token:
            try:
                # Add token to the blacklist
                RevokedToken.objects.create(token=token)
                return Response({'message': 'Successfully logged out.'})
            except Exception as e:
                return Response({'error': str(e)}, status=500)
        else:
            return Response({'error': 'No token provided'}, status=400)
