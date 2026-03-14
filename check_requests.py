import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import PrincipalRequest

requests = PrincipalRequest.objects.all()
print(f"Total requests: {requests.count()}")
for r in requests:
    code = r.college_name.lower().replace(" ", "_")
    print(f"ID: {r.id} | Name: {r.college_name} | Code: {code} | Length: {len(code)}")
