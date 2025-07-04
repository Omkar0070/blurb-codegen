import os
import sys
from github import Github
import openai

REPO = os.getenv("GITHUB_REPOSITORY")
DISCUSSION_CATEGORY = "Blurb"

def fetch_blurb():
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(REPO)
    discussions = repo.get_discussions()
    for d in discussions:
        if d.category.name == DISCUSSION_CATEGORY and "🟢" in d.title:
            with open("blurb.txt", "w") as f:
                f.write(d.body)
            print("✅ Blurb found:", d.title)
            return
    raise Exception("❌ No blurb found.")

def generate_code():
    with open("blurb.txt") as f:
        prompt = f.read()

    openai.api_key = os.environ["OPENAI_API_KEY"]
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You generate clean and functional code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    code = res["choices"][0]["message"]["content"]
    os.makedirs("generated", exist_ok=True)
    with open("generated/add.cs", "w") as f:
        f.write(code)
    print("✅ Code written to generated/add.cs")

def compile_code():
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

