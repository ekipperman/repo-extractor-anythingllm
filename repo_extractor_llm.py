import os
import requests
from github import Github

# Environment Variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY")
ANYTHINGLLM_URL = os.getenv("ANYTHINGLLM_URL", "https://your-anythingllm-instance.com/api")
ORG_NAME = os.getenv("ORG_NAME")
REPO_NAME = os.getenv("REPO_NAME")

# Validate env vars
if not all([GITHUB_TOKEN, ANYTHINGLLM_API_KEY, ANYTHINGLLM_URL, ORG_NAME, REPO_NAME]):
    raise Exception("🚨 One or more required environment variables are missing!")

# Initialize GitHub API
github = Github(GITHUB_TOKEN)
repo = github.get_repo(f"{ORG_NAME}/{REPO_NAME}")

# Define which files/folders to extract
TARGET_FILES = ["README.md", "docs/", "config.json", "api/", "src/"]

def fetch_repo_files(path=""):
    """Fetch relevant files from the GitHub repository recursively."""
    extracted_data = {}
    contents = repo.get_contents(path)

    for content in contents:
        if content.type == "dir":
            extracted_data.update(fetch_repo_files(content.path))
        elif any(target in content.path for target in TARGET_FILES):
            extracted_data[content.path] = content.decoded_content.decode()

    return extracted_data

def create_workspace():
    """Create a new workspace in AnythingLLM."""
    headers = {
        "Authorization": f"Bearer {ANYTHINGLLM_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "name": REPO_NAME
    }

    response = requests.post(f"{ANYTHINGLLM_URL}/workspaces", headers=headers, json=data)
    
    if response.status_code == 200:
        workspace = response.json()
        print(f"✅ Workspace '{REPO_NAME}' created! ID: {workspace.get('id')}")
        return workspace.get("id")
    else:
        raise Exception(f"❌ Workspace creation failed: {response.status_code}, {response.text}")

def upload_documents(workspace_id, extracted_data):
    """Upload extracted files to the new workspace."""
    headers = {
        "Authorization": f"Bearer {ANYTHINGLLM_API_KEY}",
        "Content-Type": "application/json"
    }

    for path, content in extracted_data.items():
        doc_payload = {
            "name": path,
            "content": content
        }

        response = requests.post(
            f"{ANYTHINGLLM_URL}/workspaces/{workspace_id}/documents",
            headers=headers,
            json=doc_payload
        )

        if response.status_code == 200:
            print(f"✅ Uploaded {path} to workspace!")
        else:
            print(f"❌ Failed to upload {path}: {response.status_code}, {response.text}")

def trigger_ai_training(workspace_id):
    """Trigger AI Agent Training after data upload."""
    headers = {"Authorization": f"Bearer {ANYTHINGLLM_API_KEY}"}
    
    response = requests.post(f"{ANYTHINGLLM_URL}/workspaces/{workspace_id}/train", headers=headers)
    
    if response.status_code == 200:
        print("✅ AI Training Successfully Triggered!")
    else:
        print(f"❌ AI Training failed: {response.status_code}, {response.text}")

def main():
    print("🚀 Starting Automated Workspace Creation and Repo Extraction...")
    
    # Step 1: Create Workspace
    workspace_id = create_workspace()
    
    # Step 2: Fetch repo data
    repo_data = fetch_repo_files()
    if not repo_data:
        print("⚠️ No files matched the target filters.")
        return
    
    # Step 3: Upload files to AnythingLLM Workspace
    upload_documents(workspace_id, repo_data)
    
    # Step 4: Trigger AI Training
    trigger_ai_training(workspace_id)

    print("✅ Process Completed!")

if __name__ == "__main__":
    main()
