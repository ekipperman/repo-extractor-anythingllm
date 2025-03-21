import os
import requests
from github import Github
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY")
ANYTHINGLLM_URL = os.getenv("ANYTHINGLLM_URL", "https://your-anythingllm-instance.com/api")
ORG_NAME = os.getenv("ORG_NAME")
REPO_NAME = os.getenv("REPO_NAME")
CLIENT_NAME = os.getenv("CLIENT_NAME", "default-client")
WORKSPACE_TAGS = os.getenv("WORKSPACE_TAGS", "automation,extraction")

# Validate environment variables
required_vars = [GITHUB_TOKEN, ANYTHINGLLM_API_KEY, ANYTHINGLLM_URL, ORG_NAME, REPO_NAME]
if not all(required_vars):
    raise Exception("❌ One or more required environment variables are missing!")

# Initialize GitHub API
github = Github(GITHUB_TOKEN)
repo = github.get_repo(f"{ORG_NAME}/{REPO_NAME}")

print(f"✅ Connected to repository: {repo.full_name}")

# Define which files/folders to extract
TARGET_FILES = ["README.md", "docs/", "config.json", "api/", "src/"]

def fetch_repo_files(path=".", depth=0):
    """Recursively fetch relevant files from GitHub repository."""
    extracted_data = {}
    contents = repo.get_contents(path)

    for content in contents:
        if content.type == "dir":
            extracted_data.update(fetch_repo_files(content.path, depth+1))
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

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        workspace = response.json()
        print(f"✅ Workspace '{CLIENT_NAME}' created!")
        return workspace['id']
    elif response.status_code == 409:
        print(f"⚠️ Workspace '{CLIENT_NAME}' already exists. Skipping creation.")
        return None
    else:
        print(f"❌ Failed to create workspace: {response.status_code} {response.text}")
        return None

def upload_to_anythingllm(workspace_id, extracted_data):
    """Upload extracted data to AnythingLLM."""
    url = f"{ANYTHINGLLM_URL}/workspaces/{workspace_id}/documents"
    headers = {"Authorization": f"Bearer {ANYTHINGLLM_API_KEY}"}
    documents = [{"name": path, "content": content} for path, content in extracted_data.items()]
    
    response = requests.post(url, headers=headers, json={"documents": documents})
    
    if response.status_code == 200:
        print("✅ Successfully uploaded documents to AnythingLLM!")
    else:
        print(f"❌ Upload failed: {response.status_code} {response.text}")

def trigger_ai_training(workspace_id):
    """Trigger AI Agent Training in AnythingLLM."""
    url = f"{ANYTHINGLLM_URL}/workspaces/{workspace_id}/train"
    headers = {"Authorization": f"Bearer {ANYTHINGLLM_API_KEY}"}

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        print("✅ AI Training successfully triggered!")
    else:
        print(f"❌ AI Training failed: {response.status_code} {response.text}")

def main():
    print("🚀 Starting Repo Extraction and AnythingLLM Integration...")

    workspace_id = create_workspace()
    if not workspace_id:
        print("❌ Workspace creation failed or already exists. Aborting.")
        return

    repo_data = fetch_repo_files()
    
    if not repo_data:
        print("⚠️ No matching files found for extraction.")
        return

    upload_to_anythingllm(workspace_id, repo_data)
    trigger_ai_training(workspace_id)

    print("✅ Process Completed!")

if __name__ == "__main__":
    main()
