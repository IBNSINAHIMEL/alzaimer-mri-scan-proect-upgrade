import requests
import os

# Create directory
os.makedirs('static/css', exist_ok=True)

# Download Tailwind CSS
print("📥 Downloading Tailwind CSS...")
url = 'https://cdn.tailwindcss.com'
response = requests.get(url)

if response.status_code == 200:
    with open('static/css/tailwind.min.css', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("✅ Tailwind CSS downloaded successfully!")
    print("📁 Saved to: static/css/tailwind.min.css")
else:
    print("❌ Failed to download Tailwind CSS")