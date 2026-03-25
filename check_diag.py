import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import SpottingBank

output_file = 'spotting_diag_root.txt'

with open(output_file, 'w') as f:
    f.write("--- Records ---\n")
    for item in SpottingBank.objects.all():
        f.write(f"Name: {item.name}, Slug: {item.image_slug}\n")
    f.write("--- Files ---\n")
    if os.path.exists("static/spotting_images"):
        f.write(str(os.listdir("static/spotting_images")))
    else:
        f.write("Directory not found")

print("Done")
