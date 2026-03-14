import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
print(f"Django Version: {django.get_version()}")
from accounts.models import College
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT column_name, character_maximum_length FROM information_schema.columns WHERE table_name = 'accounts_college' AND column_name = 'code';")
    row = cursor.fetchone()
    print(f"College.code length in DB: {row}")

from experiments.views_superadmin_ui import approve_principal_request
import inspect
print(f"Source of approve_principal_request:\n{inspect.getsource(approve_principal_request)}")
