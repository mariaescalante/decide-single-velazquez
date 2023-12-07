from django.core.mail import send_mail
from django.template.loader import render_to_string
from utils.datetimes import get_datetime_now_formatted

def send_email_login_notification(request, template, subject):
    user = request.user

    # Datos de interes para el correo
    direccion_ip = request.META.get('REMOTE_ADDR')
    agente_usuario = request.META.get('HTTP_USER_AGENT')
    fecha_formateada = get_datetime_now_formatted()

    context = {
        'nombre': user.username,
        'direccion_ip': direccion_ip,
        'agente_usuario': agente_usuario,
        'fecha_actual': fecha_formateada
    }

    html_message = render_to_string(template, context)

    # Configuracion del correo
    subject = subject
    from_email = 'decidevelazquez@gmail.com'
    recipient_list = [user.email]

    send_mail(subject, '', from_email, recipient_list, html_message=html_message)