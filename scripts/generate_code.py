import os
import sys
import requests
from openai import OpenAI

REPO = os.getenv("GITHUB_REPOSITORY")
OWNER, NAME = REPO.split("/")
DISCUSSION_CATEGORY = "Blurb"

def fetch_blurb():
    print("🔍 Fetching discussion blurb from GitHub GraphQL...")

    query = f"""
    {{
      repository(owner: "{OWNER}", name: "{NAME}") {{
        discussions(first: 10, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
          nodes {{
            title
            body
            number
            category {{
              name
            }}
          }}
        }}
      }}
    }}
    """
    headers = {
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"
    }

    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query},
        headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"❌ GraphQL query failed: {response.status_code} - {response.text}")

    data = response.json()
    discussions = data["data"]["repository"]["discussions"]["nodes"]

    print("📝 Fetched Discussions:")
    for d in discussions:
        print(f" - Title: {d['title']} | Category: {d['category']['name']}")
        if d["category"]["name"] == DISCUSSION_CATEGORY:
            with open("blurb.txt", "w") as f:
                f.write(d["body"])
            print(f"✅ Found blurb: {d['title']}")
            return

    raise Exception("❌ No matching blurb found.")

def generate_code():
    print("🧠 Generating code using OpenAI GPT...")
    with open("blurb.txt") as f:
        prompt = f.read()

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You generate clean and functional code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    code = response.choices[0].message.content

    os.makedirs("generated", exist_ok=True)
    with open("generated/add.cs", "w") as f:
        f.write(code)
    print("✅ Code written to generated/add.cs")

def compile_code():
    print("⚙️ Compiling generated C# code...")
    os.makedirs("project", exist_ok=True)
    os.chdir("project")
    os.system("dotnet new classlib -n CodeGen")
    os.system("mv ../generated/add.cs CodeGen/")
    os.chdir("CodeGen")
    code = os.system("dotnet build")
    if code != 0:
        raise Exception("❌ Build failed")
    else:
        print("✅ Build succeeded")

if __name__ == "__main__":
    action = sys.argv[1]
    if action == "fetch":
        fetch_blurb()
    elif action == "generate":
        generate_code()
    elif action == "compile":
        compile_code()
