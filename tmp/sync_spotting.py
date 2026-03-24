import os
import sys
import django

# Add current directory to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
    from experiments.models import SpottingBank
except Exception as e:
    print(f"Error during Django setup: {e}")
    sys.exit(1)

def sync_spotting():
    # Path to spotting images
    img_dir = 'static/spotting_images'
    
    if not os.path.exists(img_dir):
        print(f"Directory not found: {img_dir}")
        return

    # Get list of files in directory
    files = [f for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))]
    
    print(f"Found {len(files)} images in {img_dir}")
    
    if len(files) == 0:
        print("No images found to sync.")
        return

    try:
        # Delete existing entries (or you could filter)
        # The user said they deleted old images, so we should refresh the bank
        count, _ = SpottingBank.objects.all().delete()
        print(f"Deleted {count} old spotting bank entries")
        
        # Add new entries
        for i, filename in enumerate(sorted(files), 1):
            # Create a friendly name, e.g., Specimen 1, Specimen 2
            name = f"Specimen {i}"
            
            SpottingBank.objects.create(
                name=name,
                image_slug=filename,
                is_active=True
            )
            print(f"Added: {name} ({filename})")
        print("Sync completed successfully.")
    except Exception as e:
        print(f"Error during database operation: {e}")

if __name__ == "__main__":
    sync_spotting()
