from datetime import datetime
import pytz

def get_datetime_now_formatted():
    # Crea un objeto datetime en UTC
    fecha_hora_utc = datetime.utcnow()

    # Asigna la zona horaria a UTC
    fecha_hora_utc = pytz.utc.localize(fecha_hora_utc)

    # Convierte a la zona horaria local de Madrid
    zona_horaria_local = pytz.timezone('Europe/Madrid')
    fecha_hora_local = fecha_hora_utc.astimezone(zona_horaria_local)

    # Formatea la fecha y hora según el formato deseado
    formato_deseado = "%B %d at %I:%M %p"
    fecha_formateada = fecha_hora_local.strftime(formato_deseado)
    
    return fecha_formateada