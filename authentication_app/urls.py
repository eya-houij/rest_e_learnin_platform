from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [

    # Path for user login
    path('login/', views.UserLoginView.as_view(), name='user-login'),

    # Path for user registration
    path('register/', views.UserRegistrationView.as_view(), name='user-registration'),

    # Path for user logout
    path('logout/', views.LogoutView.as_view(), name='user-logout'),

    # ...
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # ...
    
]
