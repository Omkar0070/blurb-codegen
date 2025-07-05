import os
import sys
from openai import OpenAI
import requests

# Initialize OpenAI client using environment variable
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Get GitHub repository context
REPO = os.getenv("GITHUB_REPOSITORY")
OWNER, NAME = REPO.split("/")
DISCUSSION_CATEGORY = "Blurb"  # Ensure this matches your Discussion category in GitHub

def fetch_blurb():
    print("🔍 Fetching discussion blurb from GitHub GraphQL...")

    # GitHub GraphQL query to fetch recent discussions
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

    # Call GitHub GraphQL API
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

    # Find first discussion matching 'Blurb' category
    for d in discussions:
        if d["category"]["name"].lower() == DISCUSSION_CATEGORY.lower():
            with open("blurb.txt", "w") as f:
                f.write(d["body"])
            print(f"✅ Found blurb: {d['title']}")
            return

    raise Exception("❌ No matching blurb found in 'Blurb' category.")

def generate_code():
    print("🧠 Generating code using OpenAI GPT...")

    with open("blurb.txt") as f:
        prompt = f.read()

    # Call OpenAI ChatCompletion API to generate C# code only
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You generate clean and functional C# code only. No explanations or markdown formatting."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    code = res.choices[0].message.content

    # ✅ Clean output: remove markdown fences and explanation if any
    if "```" in code:
        code = code.split("```")[1]
        lines = code.splitlines()
        if lines[0].strip().startswith("csharp"):
            lines = lines[1:]  # remove ```csharp line
        code = "\n".join(lines)

    os.makedirs("generated", exist_ok=True)
    with open("generated/add.cs", "w") as f:
        f.write(code.strip())

    print("✅ Clean C# code written to generated/add.cs")

def compile_code():
    print("⚙️ Compiling generated C# code using dotnet...")

    os.makedirs("project", exist_ok=True)
    os.chdir("project")
    os.system("dotnet new classlib -n CodeGen --force")
    os.system("mv ../generated/add.cs CodeGen/")
    os.chdir("CodeGen")
    result = os.system("dotnet build")

    if result != 0:
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
    else:
        print("❌ Unknown action. Use: fetch, generate, or compile.")
