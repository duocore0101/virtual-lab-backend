import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import SpottingBank
print(f"Count: {SpottingBank.objects.count()}")
for item in SpottingBank.objects.all()[:5]:
    print(f"- {item.name}: {item.image_slug}")
