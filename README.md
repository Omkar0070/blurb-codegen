# 🚀 Blurb CodeGen CI/CD Pipeline

This project automates **C# code generation** from GitHub Discussions using OpenAI GPT, compiles the code, and creates a Pull Request for review.

---

## ✨ **Features**

- Fetches discussion blurbs from GitHub Discussions (category: Blurb)
- Generates functional C# code using OpenAI GPT-4o
- Compiles code with .NET SDK to ensure build integrity
- Pushes to a unique feature branch
- Creates a Pull Request targeting `main`

---

## 📋 **Prerequisites**

- GitHub repository with Discussions enabled
- [GitHub Actions](https://docs.github.com/actions) configured
- OpenAI API Key (GPT-4o model access)
- GitHub Personal Access Token (GH_PAT) with `repo` scope for PR creation via CLI

---

## ⚙ **Setup**

1. **Secrets configuration**

In your repository settings, add:

| Name             | Description                   |
| ---------------- | ----------------------------- |
| `OPENAI_API_KEY` | OpenAI API key with GPT-4o access |
| `GH_PAT`         | GitHub Personal Access Token with repo scope |

2. **Workflow trigger**

Run manually via **Actions > Blurb → Code → Compile → PR > Run workflow**.

---

## 🛠️ **CI/CD Pipeline Flow**

1. **Workflow dispatch triggered**
2. Repository is checked out
3. Python and .NET SDK are setup
4. Python dependencies (`openai`, `requests`) are installed
5. `scripts/generate_code.py` runs:
    - Fetches discussion blurb
    - Generates code via OpenAI
    - Compiles with dotnet
6. Generated code is committed to a new feature branch
7. GitHub CLI (`gh`) creates a Pull Request to `main`.

---

## 🚀 **Usage**

1. Create a new **Discussion** in category **Blurb** with your code generation prompt.
2. Trigger the workflow manually.
3. Review the generated PR and merge if valid.

---

## 📄 **License**

MIT

---

## 🙌 **Contributors**

- Omkar Kadam (DevOps Engineer, Automation Developer)

---

> **Note:** This pipeline is designed for educational and automation demo purposes. Production deployments should include additional tests, code linting, and branch protection rules.
