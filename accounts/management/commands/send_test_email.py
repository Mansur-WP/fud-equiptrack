from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Sends a test email to verify SMTP configuration.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='The destination email address.')

    def handle(self, *args, **options):
        email = options['email']
        subject = 'Test Email from FUD-IERMS'
        message = 'This is a test email sent from the Django management command to verify Resend SMTP configuration.'
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully sent test email to {email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email. Error: {e}'))
