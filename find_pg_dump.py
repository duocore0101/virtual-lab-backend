import os

search_paths = [
    r"C:\Program Files\PostgreSQL",
    r"C:\Program Files (x86)\PostgreSQL"
]

found = False
for path in search_paths:
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            if "pg_dump.exe" in files:
                print(os.path.join(root, "pg_dump.exe"))
                found = True
                break
    if found:
        break

if not found:
    print("NOT_FOUND")
