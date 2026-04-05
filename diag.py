import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtual_lab.settings')
django.setup()
print("Django setup success")
