#!/usr/bin/env python3

import os
import requests

# Get environment variables from GitHub Actions
OWNER = os.getenv("OWNER")
REPO = os.getenv("REPO")
CATEGORY = os.getenv("CATEGORY_NAME")
TOKEN = os.getenv("GITHUB_TOKEN")

# GitHub REST API endpoint for discussions
url = f"https://api.github.com/repos/{OWNER}/{REPO}/discussions"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Fetch discussions from GitHub
resp = requests.get(url, headers=headers)

# Handle failure to fetch discussions
if resp.status_code != 200:
    print("❌ Failed to fetch discussions")
    open("new_blurb_flag.txt", "w").write("false")
    exit(0)

# Parse discussions JSON
data = resp.json()

# Find latest discussion in the target category
latest = next(
    (d for d in data if d.get("category", {}).get("name", "").lower() == CATEGORY.lower()),
    None
)

# If no matching discussion found
if not latest:
    print("ℹ️ No discussion found in the specified category.")
    open("new_blurb_flag.txt", "w").write("false")
    exit(0)

# Check previously seen discussion number
last_id = 0
if os.path.exists(".last-discussion-id"):
    with open(".last-discussion-id") as f:
        last_id = int(f.read().strip())

# If a new discussion is found
if latest["number"] > last_id:
    print(f"🆕 New discussion detected: {latest['title']}")
    with open("blurb.txt", "w") as f:
        f.write(latest["body"])
    with open(".last-discussion-id", "w") as f:
        f.write(str(latest["number"]))
    open("new_blurb_flag.txt", "w").write("true")
else:
    print("✅ No new discussions since last check.")
    open("new_blurb_flag.txt", "w").write("false")
