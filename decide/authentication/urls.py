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
    path('2fa/<int:user_id>/', dobleautenticacion),
    path('segunda/<int:user_id>/', comprobarqr, name='comprobarqr'),
    path('logout2/', logout_then_login, name="logout"),
    path('login2/', Custom_loginView.as_view(), name='login'),
    path('registerEmail/', registroEmail, name="registroEmail"),


]