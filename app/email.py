from flask_mail import Message
from mail import mail


def send_email(to, subject, message):
    msg = Message(subject=subject,
                  recipients=[to],
                  body=message)
    mail.send(msg)
