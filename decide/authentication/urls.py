from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import logout_then_login
from .views import *
from .views import CertLoginView

urlpatterns = [
    path('dashboard/', home, name='home'),
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('cert_login/', CertLoginView.as_view(), name='cert_login'),
    path('register/', RegisterView.as_view()),
    path('register2/', registro, name="registro"),
    path('2fa/<int:user_id>/', dobleautenticacion),
    path('segunda/<int:user_id>/', comprobarqr, name='comprobarqr'),
    path('logout2/', logout_then_login, name="logout"),
    path('login2/', Custom_loginView.login2, name='login2'),
    path('cuenta/', cuenta, name='cuenta'),
    path('cuenta/editar_perfil/', editar_perfil, name='editar_perfil'),
    path('register_email/', registro_email, name="registro_email"),
    path('password_reset2/', CustomPasswordResetView.as_view(), name='password_reset2'),
    path('password_reset2/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done2'),
    path('reset2/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm2'),
    path('reset2/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete2'),
    path('2faquit/<int:user_id>/', quitardobleautenticacion, name='password_reset_complete2'),
    path('password-change2/', CustomPasswordChangeView.as_view(), name='password_change2'),
    path('password-change2/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_success2'),
    path('confirmar_borrar_cuenta/', confirmar_borrar_cuenta, name='confirmar_borrar_cuenta'),
    path('borrar_cuenta/', borrar_cuenta, name='borrar_cuenta'),
]