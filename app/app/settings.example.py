from app.settings_shared import *

# Copy this file to `settings.py` and fill out with your variables

RESOLUTION = '3280:2464'  # 2592x1944
FTP_SERVER = 'ftp.example.com'
FTP_USER = 'myuser'
FTP_PASS = 'secret'
FTP_DESTINATION_DIR = 'My-Pi-Name'
ADMINS = (('Name', 'email_address'),)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.example.net'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'user@example.net'
EMAIL_HOST_PASSWORD = 'asdfasdf'
EMAIL_USE_SSL = True
SERVER_EMAIL = 'django@localhost'  # For mails to admins via `mail_admins()`
EMAIL_SUBJECT_PREFIX = '[MySite] '  # For `mail_admins()`
DEFAULT_FROM_EMAIL = 'support@example.com'  # For mails to users via `send_mail()`