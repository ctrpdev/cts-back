from django.core.mail import send_mail
from celery import shared_task


@shared_task()
def send_verification_email(verification_link, email):
    send_mail(
        'Verifica tu cuenta',
        f'Por favor, verifica tu cuenta haciendo clic en el siguiente enlace: {verification_link}',
        'ctrpdev@gmail.com',
        [email],
        fail_silently=False,
    )


@shared_task()
def send_winner_notification(first_name, last_name, email):
    try:
        send_mail(
            '¡Felicidades! Has ganado el sorteo',
            f'Hola {first_name} {last_name},\n\n¡Felicidades! Has sido seleccionado como el ganador del sorteo. Por favor, contacta con nosotros para más detalles.',
            'ctrpdev@gmail.com',
            [email],
            fail_silently=False,
        )
    except Exception as e:
        print(f'Error al enviar correo: {str(e)}')
