from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import logout_then_login
from .views import *
from .views import Custom_loginView

urlpatterns = [
    path('dashboard/', home, name='home'),
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', registro, name="registro"),
    path('custom_login/', CustomLoginView.as_view(), name='custom_login'),
]