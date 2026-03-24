import os

root_dir = r"d:\virtual-lab-backend\templates\experiments"
old_text = "/student/dashboard/"
new_text = "{{ dashboard_url }}"

for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if old_text in content:
                new_content = content.replace(old_text, new_text)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated: {path}")
