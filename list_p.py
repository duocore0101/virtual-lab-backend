import os
files = os.listdir("C:\\Program Files")
for f in files:
    if "PostgreSQL" in f:
        print(f)
