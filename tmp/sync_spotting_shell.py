import os
from experiments.models import SpottingBank

def sync_spotting():
    img_dir = 'static/spotting_images'
    if not os.path.exists(img_dir):
        print(f"Directory not found: {img_dir}")
        return

    files = [f for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))]
    print(f"Found {len(files)} images in {img_dir}")

    if len(files) == 0:
        print("No images found to sync.")
        return

    # Delete existing entries
    count, _ = SpottingBank.objects.all().delete()
    print(f"Deleted {count} old spotting bank entries")

    # Add new entries
    for i, filename in enumerate(sorted(files), 1):
        name = f"Specimen {i}"
        SpottingBank.objects.create(
            name=name,
            image_slug=filename,
            is_active=True
        )
        print(f"Added: {name} ({filename})")
    print("Sync completed successfully.")

sync_spotting()
