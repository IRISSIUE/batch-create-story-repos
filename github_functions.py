import os
import requests
from github import Github

# Global variables
GH = None
GITHUB_TOKEN = None

def login_to_github():
    """Authenticate to GitHub using a personal access token."""
    global GH, GITHUB_TOKEN
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN is not set in your environment.")
        print("A Github Personal Access Token is required to access the existing template repository" \
            " and to create the new repositories.")
        print("The Github account associated with the token must have access to " \
                " both the template repository and the organization where you will create the new repositories.")
        print("You can set the token in your enviornment by invoking the commands:")
        print("Unix/Linux/macOS: 'export GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXX'")
        print("Windows: 'set GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXX' or '$env:GITHUB_TOKEN=""ghp_XXXXXXXXXXXXXXXXXX""' ")
        exit(1)

    # This authenticates (logs in) the user using the provided token
    GH = Github(GITHUB_TOKEN)
    user = GH.get_user()
    print(f"Authenticed as GitHub User: {user.login} ({user.name})")

    

def create_repo_from_template(template_path, batch_repo_owner, batch_repo_name, batch_repo_description):
    
    print(f"Attempting to create GitHub repo {batch_repo_name} from template {template_path}...")

    url = f"https://api.github.com/repos/{template_path}/generate"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
    }

    data = {
        "owner": batch_repo_owner,
        "name": batch_repo_name,
        "description": batch_repo_description,
        "private": False
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print("Succesfully created repository :", response.json()["html_url"])
    else:
        print("Failed to create repo:", response.status_code)
        print(response.json())
        return None

    new_repo = GH.get_repo(f"{batch_repo_owner}/{batch_repo_name}")
    return new_repo

