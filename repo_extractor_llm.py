import os
import requests
from github import Github

# Environment Variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY")
ANYTHINGLLM_URL = os.getenv("ANYTHINGLLM_URL", "https://your-anythingllm-instance.com/api")

# GitHub Repo Config
ORG_NAME = "your-github-org"
REPO_NAME = "your-client-repo"

# Initialize GitHub API
github = Github(GITHUB_TOKEN)
repo = github.get_repo(f"{ORG_NAME}/{REPO_NAME}")

# Define which files/folders to extract
TARGET_FILES = ["README.md", "docs/", "config.json", "api/", "src/"]

def fetch_repo_files():
    """Fetch relevant files from the GitHub repository."""
    extracted_data = {}
    contents = repo.get_contents(".")
    
    for content in contents:
        if any(target in content.path for target in TARGET_FILES):
            extracted_data[content.path] = content.decoded_content.decode()
    
    return extracted_data

def format_data_for_anythingllm(extracted_data):
    """Format extracted data into AnythingLLM-compatible JSON."""
    return {
        "workspace_name": REPO_NAME,
        "documents": [
            {"name": path, "content": content} for path, content in extracted_data.items()
        ]
    }

def upload_to_anythingllm(formatted_data):
    """Upload extracted & formatted data to AnythingLLM API."""
    headers = {"Authorization": f"Bearer {ANYTHINGLLM_API_KEY}", "Content-Type": "application/json"}
    response = requests.post(f"{ANYTHINGLLM_URL}/upload", headers=headers, json=formatted_data)
    
    if response.status_code == 200:
        print("✅ Successfully uploaded data to AnythingLLM!")
    else:
        print(f"❌ Upload failed: {response.status_code}, {response.text}")

def trigger_ai_training():
    """Trigger AI Agent Training after data upload."""
    headers = {"Authorization": f"Bearer {ANYTHINGLLM_API_KEY}"}
    response = requests.post(f"{ANYTHINGLLM_URL}/train", headers=headers)
    
    if response.status_code == 200:
        print("✅ AI Training Successfully Triggered!")
    else:
        print(f"❌ AI Training failed: {response.status_code}, {response.text}")

def main():
    print("🚀 Starting Repo Extraction & LLM Integration...")
    repo_data = fetch_repo_files()
    formatted_data = format_data_for_anythingllm(repo_data)
    upload_to_anythingllm(formatted_data)
    trigger_ai_training()
    print("✅ Process Completed!")

if __name__ == "__main__":
    main()
