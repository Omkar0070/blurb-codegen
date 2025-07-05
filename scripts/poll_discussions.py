import os
import requests

OWNER = os.getenv("OWNER")
REPO = os.getenv("REPO")
CATEGORY = os.getenv("CATEGORY_NAME")
TOKEN = os.getenv("GITHUB_TOKEN")

url = f"https://api.github.com/repos/{OWNER}/{REPO}/discussions"
headers = {
"Authorization": f"Bearer {TOKEN}",
"Accept": "application/vnd.github.v3+json"
}

resp = requests.get(url, headers=headers)
if resp.status_code != 200:
print("❌ Failed to fetch discussions")
open("new_blurb_flag.txt", "w").write("false")
exit(0)

data = resp.json()
latest = next((d for d in data if d["category"]["name"].lower() == CATEGORY.lower()), None)

if not latest:
open("new_blurb_flag.txt", "w").write("false")
exit(0)

last_id = 0
if os.path.exists(".last-discussion-id"):
with open(".last-discussion-id") as f:
last_id = int(f.read().strip())

if latest["number"] > last_id:
print(f"🆕 New discussion detected: {latest['title']}")
with open("blurb.txt", "w") as f:
f.write(latest["body"])
with open(".last-discussion-id", "w") as f:
f.write(str(latest["number"]))
open("new_blurb_flag.txt", "w").write("true")
else:
open("new_blurb_flag.txt", "w").write("false")
