import os
import requests
from github import Github
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Environment Variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY")
ANYTHINGLLM_URL = os.getenv("ANYTHINGLLM_URL", "https://your-anythingllm-instance.com/api")

# ✅ Custom Variables
ORG_NAME = os.getenv("ORG_NAME")
REPO_NAME = os.getenv("REPO_NAME")
CLIENT_NAME = os.getenv("CLIENT_NAME", "default-client")  # Optional, fallback
WORKSPACE_TAGS = os.getenv("WORKSPACE_TAGS", "automation,extraction")  # Comma-separated string

# ✅ Debug Prints to Confirm
print("------------ ENVIRONMENT VARIABLES ------------")
print(f"GITHUB_TOKEN: {'SET ✅' if GITHUB_TOKEN else '❌ MISSING'}")
print(f"ANYTHINGLLM_API_KEY: {'SET ✅' if ANYTHINGLLM_API_KEY else '❌ MISSING'}")
print(f"ANYTHINGLLM_URL: {ANYTHINGLLM_URL}")
print(f"ORG_NAME: {ORG_NAME}")
print(f"REPO_NAME: {REPO_NAME}")
print(f"CLIENT_NAME: {CLIENT_NAME}")
print(f"WORKSPACE_TAGS: {WORKSPACE_TAGS}")
print("------------------------------------------------")

# ✅ Validate Environment Variables
required_vars = [GITHUB_TOKEN, ANYTHINGLLM_API_KEY, ANYTHINGLLM_URL, ORG_NAME, REPO_NAME]
if not all(required_vars):
    raise Exception("❌ One or more required environment variables are missing!")

# ✅ Initialize GitHub API and Get Repo
github = Github(GITHUB_TOKEN)

repo_path = f"{ORG_NAME}/{REPO_NAME}"
print(f"🔍 Trying to get repo: {repo_path}")

try:
    repo = github.get_repo(repo_path)
    print(f"✅ Connected to repository: {repo.full_name}")
except Exception as e:
    print(f"❌ Failed to get repository: {e}")
    exit(1)

# ✅ Define Which Files/Folders to Extract
TARGET_FILES = ["README.md", "docs/", "config.json", "api/", "src/"]

def fetch_repo_files(path=".", depth=0):
    """Recursively fetch relevant files from GitHub repository."""
    extracted_data = {}
    try:
        contents = repo.get_contents(path)
    except Exception as e:
        print(f"❌ Error fetching contents at path '{path}': {e}")
        return extracted_data

    for content in contents:
        if content.type == "dir":
            extracted_data.update(fetch_repo_files(content.path, depth + 1))
        elif any(target in content.path for target in TARGET_FILES):
            print(f"📄 Extracting {content.path}")
            extracted_data[content.path] = content.decoded_content.decode()

    return extracted_data

def create_workspace():
    """Create a workspace in AnythingLLM."""
    url = f"{ANYTHINGLLM_URL}/workspaces"
    headers = {"Authorization": f"Bearer {ANYTHINGLLM_API_KEY}"}
    data = {
        "name": CLIENT_NAME,
        "tags": WORKSPACE_TAGS.split(",")
    }

    print(f"🔧 Creating workspace '{CLIENT_NAME}' at {url}...")
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        workspace = response.json()
        print(f"✅ Workspace '{CLIENT_NAME}' created! Workspace ID: {workspace['id']}")
        return workspace['id']
    elif response.status_code == 409:
        print(f"⚠️ Workspace '{CLIENT_NAME}' already exists. Skipping creation.")
        # You may want to fetch the existing workspace ID here in a real scenario
        return None
    else:
        print(f"❌ Failed to create workspace: {response.status_code} {response.text}")
        return None

def upload_to_anythingllm(workspace_id, extracted_data):
    """Upload extracted data to AnythingLLM."""
    url = f"{ANYTHINGLLM_URL}/workspaces/{workspace_id}/documents"
    headers = {"Authorization": f"Bearer {ANYTHINGLLM_API_KEY}"}
    documents = [{"name": path, "content": content} for path, content in extracted_data.items()]

    print(f"📤 Uploading {len(documents)} documents to workspace ID {workspace_id}...")
    response = requests.post(url, headers=headers, json={"documents": documents})

    if response.status_code == 200:
        print("✅ Successfully uploaded documents to AnythingLLM!")
    else:
        print(f"❌ Upload failed: {response.status_code} {response.text}")

def trigger_ai_training(workspace_id):
    """Trigger AI Agent Training in AnythingLLM."""
    url = f"{ANYTHINGLLM_URL}/workspaces/{workspace_id}/train"
    headers = {"Authorization": f"Bearer {ANYTHINGLLM_API_KEY}"}

    print(f"🚀 Triggering AI training on workspace ID {workspace_id}...")
    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        print("✅ AI Training successfully triggered!")
    else:
        print(f"❌ AI Training failed: {response.status_code} {response.text}")

def main():
    print("🚀 Starting Repo Extraction and AnythingLLM Integration...")

    # Step 1: Create a workspace
    workspace_id = create_workspace()
    if not workspace_id:
        print("❌ Workspace creation failed or already exists. Aborting.")
        return

    # Step 2: Fetch repo data
    repo_data = fetch_repo_files()

    if not repo_data:
        print("⚠️ No matching files found for extraction.")
        return

    # Step 3: Upload data
    upload_to_anythingllm(workspace_id, repo_data)

    # Step 4: Trigger training
    trigger_ai_training(workspace_id)

    print("✅ Process Completed!")

if __name__ == "__main__":
    main()
