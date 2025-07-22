import os
import requests

OWNER = os.getenv("OWNER")
REPO = os.getenv("REPO")
CATEGORY = os.getenv("CATEGORY_NAME")
TOKEN = os.getenv("GITHUB_TOKEN")

print(f"🔍 Checking discussions in repo: {OWNER}/{REPO}, category: {CATEGORY}")

url = f"https://api.github.com/repos/{OWNER}/{REPO}/discussions"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

resp = requests.get(url, headers=headers)
if resp.status_code != 200:
    print(f"❌ Failed to fetch discussions: {resp.status_code}")
    open("blurb.txt", "w").write("false")
    exit(0)

data = resp.json()
print(f"✅ Fetched {len(data)} discussions")

latest = next((d for d in data if d["category"]["name"].lower() == CATEGORY.lower()), None)

if not latest:
    print(f"⚠️ No discussion found in category '{CATEGORY}'")
    open("blurb.txt", "w").write("false")
    exit(0)

print(f"🆕 Latest discussion found: {latest['title']} (#{latest['number']})")

last_id = 0
if os.path.exists(".last-discussion-id"):
    with open(".last-discussion-id") as f:
        last_id = int(f.read().strip())

print(f"📁 Last recorded discussion ID: {last_id}")

if latest["number"] > last_id:
    print("✅ New discussion detected! Saving content...")
    with open("blurb.txt", "w") as f:
        f.write(latest["body"])
    with open(".last-discussion-id", "w") as f:
        f.write(str(latest["number"]))
    open("blurb.txt", "w").write("true")
else:
    print("📭 No new discussion detected.")
    open("blurb.txt", "w").write("false")
