import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def grant_permissions():
    with connection.cursor() as cursor:
        try:
            # Try to change owner or grant all
            cursor.execute("ALTER TABLE experiments_batch OWNER TO virtual_user;")
            print("Successfully changed owner of experiments_batch to virtual_user")
        except Exception as e:
            print(f"Failed to change owner: {e}")
            try:
                cursor.execute("GRANT ALL PRIVILEGES ON TABLE experiments_batch TO virtual_user;")
                print("Successfully granted privileges on experiments_batch to virtual_user")
            except Exception as e2:
                print(f"Failed to grant privileges: {e2}")

if __name__ == "__main__":
    grant_permissions()
