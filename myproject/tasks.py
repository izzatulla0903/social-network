from .celery import app
from account.send_email import send_confirmation_email 
from django.core.mail import send_mail
from account.models import Contact
@app.task 
def send_email_task(to_email, code):
    send_confirmation_email(to_email, code)

@app.task
def send_beat_email():
 for user in Contact.objects.all():
    send_mail(
        'Spam Spam Spam',
        'this is spam letter for you from NoName',
        'izzatulla.bibek@gmail.com',
        [user.email],
        fail_silently=False,
    )