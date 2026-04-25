import os
import re

base_dir = r"d:\virtual-lab-backend\templates\experiments"

# 1. Update intro.html / requirements.html for link preloading
pattern_link = re.compile(r'({% if cached_model_path %}\s*<!-- 🚀 PRELOAD 3D MODEL FOR INSTANT REQUIREMENTS PAGE -->\s*<link rel="preload" href="{% static cached_model_path %}" as="fetch" crossorigin="anonymous">\s*{% endif %})', re.DOTALL)

replacement_link = r'''\1

  {% if cached_video_paths %}
  <!-- 🚀 PRELOAD VIDEOS TO PREVENT BUFFERING DURING EXPERIMENT -->
  {% for video_path in cached_video_paths %}
  <link rel="preload" href="{% static video_path %}" as="video" type="video/mp4">
  {% endfor %}
  {% endif %}'''

# 2. Update experiment.html for video preload="auto"
pattern_video = re.compile(r'preload="metadata"')
replacement_video = 'preload="auto"'

updated_links_count = 0
updated_videos_count = 0

for root, dirs, files in os.walk(base_dir):
    for file in files:
        file_path = os.path.join(root, file)
        
        # Link preloading in intro/requirements
        if file in ["intro.html", "requirements.html"]:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if pattern_link.search(content) and "cached_video_paths" not in content:
                new_content = pattern_link.sub(replacement_link, content)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated_links_count += 1
                print(f"Updated Links: {file_path}")

        # Video preload in experiment pages
        if "experiment" in file and file.endswith(".html"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if pattern_video.search(content):
                new_content = pattern_video.sub(replacement_video, content)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated_videos_count += 1
                print(f"Updated Video Tag: {file_path}")

print(f"Total files updated (Links): {updated_links_count}")
print(f"Total files updated (Video tags): {updated_videos_count}")
