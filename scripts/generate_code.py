import os
import sys
from openai import OpenAI
import requests

# Initialize OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Get repo context from environment variables (injected by GitHub Actions)
REPO = os.getenv("GITHUB_REPOSITORY")
OWNER, NAME = REPO.split("/")
DISCUSSION_CATEGORY = "Blurb"  # Must match category name in GitHub Discussions

def fetch_blurb():
    """
    Fetches the latest discussion blurb from GitHub Discussions in the specified category
    and saves it to 'blurb.txt'.
    """
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

    # Look for first matching discussion in the specified category
    for d in discussions:
        if d["category"]["name"].lower() == DISCUSSION_CATEGORY.lower():
            with open("blurb.txt", "w", encoding="utf-8") as f:
                f.write(d["body"])
            print(f"✅ Found blurb: {d['title']}")
            return

    raise Exception(f"❌ No matching blurb found in '{DISCUSSION_CATEGORY}' category.")

def generate_code():
    """
    Generates C# code using OpenAI based on the fetched blurb prompt.
    Saves clean code to 'generated/add.cs'.
    """
    print("🧠 Generating code using OpenAI GPT...")

    if not os.path.exists("blurb.txt"):
        raise FileNotFoundError("❌ blurb.txt not found. Run fetch first.")

    with open("blurb.txt", encoding="utf-8") as f:
        prompt = f.read()

    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate clean and functional C# code only. "
                    "No explanations or markdown formatting."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    code = res.choices[0].message.content.strip()

    # ✅ Clean output to remove markdown fences if present
    if "```" in code:
        parts = code.split("```")
        code = parts[1] if len(parts) > 1 else parts[0]
        lines = code.splitlines()
        if lines and lines[0].strip().startswith("csharp"):
            lines = lines[1:]  # skip ```csharp line
        code = "\n".join(lines).strip()

    os.makedirs("generated", exist_ok=True)
    with open("generated/add.cs", "w", encoding="utf-8") as f:
        f.write(code)

    print("✅ Clean C# code written to generated/add.cs")

def compile_code():
    """
    Compiles the generated C# code using dotnet build.
    """
    print("⚙️ Compiling generated C# code...")

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
    if len(sys.argv) < 2:
        print("❌ No action provided. Use: fetch, generate, or compile.")
        sys.exit(1)

    action = sys.argv[1].lower()

    if action == "fetch":
        fetch_blurb()
    elif action == "generate":
        generate_code()
    elif action == "compile":
        compile_code()
    else:
        print("❌ Unknown action. Use: fetch, generate, or compile.")
