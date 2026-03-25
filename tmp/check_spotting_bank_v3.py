import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from experiments.models import SpottingBank

output_file = r'd:\virtual-lab-backend\tmp\spotting_diagnostic.txt'

with open(output_file, 'w') as f:
    f.write("--- SpottingBank Records ---\n")
    try:
        items = SpottingBank.objects.all()
        for item in items:
            f.write(f"Name: {item.name}, Slug: {item.image_slug}, Active: {item.is_active}\n")
    except Exception as e:
        f.write(f"Error fetching SpottingBank: {str(e)}\n")

    f.write("\n--- Files in static/spotting_images ---\n")
    static_dir = os.path.join('static', 'spotting_images')
    if os.path.exists(static_dir):
        for file_name in os.listdir(static_dir):
            f.write(f"{file_name}\n")
    else:
        f.write(f"Directory {static_dir} not found!\n")

print(f"Diagnostic completed. Results saved to {output_file}")
