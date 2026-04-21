from django.core.mail.backends.smtp import EmailBackend as SmtpBackend
from django.core.mail.backends.console import EmailBackend as ConsoleBackend

class ConsoleSmtpBackend(SmtpBackend):
    """
    Emails are sent via SMTP and also printed to the console.
    """
    def send_messages(self, email_messages):
        ConsoleBackend().send_messages(email_messages)
        return super().send_messages(email_messages)
