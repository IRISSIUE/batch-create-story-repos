import os
import requests
import base64
import re
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
                " both the template repository and the organization where you will create the new repositories (template_repo_name and batch_repo_owner in config.yaml).")
        print("You can set the token in your enviornment by invoking the commands:")
        print("Unix/Linux/macOS: 'export GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXX'")
        print("Windows: 'set GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXX' or '$env:GITHUB_TOKEN=" +'"ghp_XXXXXXXXXXXXXXXXXX"')
        exit(1)

    # This authenticates (logs in) the user using the provided token
    GH = Github(GITHUB_TOKEN)
    user = GH.get_user()
    print(f"Authenticed as GitHub User: {user.login} ({user.name})")

    
def get_repository_from_gitHub(repo_path):
    
    try:
        repo = GH.get_repo(repo_path)
    except Exception as e:
        return None
    return repo

def create_repo_from_template(template_path, batch_repo_owner, batch_repo_name, batch_repo_description) -> tuple:
    """Create a new repository from a template repository.
    
    Returns a tuple of (result, new_repo, error_message).
        result can be "created", "exists", or "error" 
        new_repo is the created repository object or None if an error occurred.
        error_message is the error message if an error occurred, otherwise None.
    """
    
    rep_path = f"{batch_repo_owner}/{batch_repo_name}"

    # Check if the repository already exists
    new_repo = get_repository_from_gitHub(rep_path)
    if new_repo:
        return ("exists", new_repo, None)

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

    if response.status_code != 201:
        return ("error", None, response.json())

    new_repo = GH.get_repo(f"{batch_repo_owner}/{batch_repo_name}")
    return ("created", new_repo, None)

def update_repo_with_google_data_sheet_link(repo, story_data_sheet_URL, file_to_update, variable_to_update) -> tuple:
    """Update the file in the repository that contains the link to the data sheet.
    
    Returns a tuple of (result, updated_file, error_message).
        result can be "updated", "no changes", or "error".
        error_message is the error message if an error occurred, otherwise None.
    """

    try:
        file = repo.get_contents(file_to_update, ref=repo.default_branch)
    except Exception as e:
        return "error", e
    
    decoded = base64.b64decode(file.content).decode("utf-8")
    lines = decoded.splitlines()
    updated_lines = update_variable_with_data_sheet_link(lines, story_data_sheet_URL, variable_to_update)

    if updated_lines == lines:
        return "no changes", None
    
    # Convert list back to string for update_file
    updated_lines = "\n".join(updated_lines)

    # --- Commit change ---
    try:
        result = repo.update_file(
            path=file_to_update,
            message="Update config with new Google Sheet URL",
            content=updated_lines,
            sha=file.sha,
            branch="main"
        )
    except Exception as e:
        return "error", e
    
    return "updated", result

def update_variable_with_data_sheet_link(lines, story_data_sheet_URL, variable_to_update) -> list:
    """Update the specified variable in the lines with the new data sheet link.
    
    Returns the updated lines if the variable was found and updated, otherwise returns the original lines.

    """
    
    updated_lines = []
    variable_found = False
    for i, line in enumerate(lines):
        match = None
        if not match and variable_to_update in line:
            # Pattern to match variable declaration with either single or double quotes
            # Captures: (everything before quotes)(quote type)(old URL)(same quote type)(everything after)
            pattern = rf'(.*{re.escape(variable_to_update)}.*?=.*?)(["\'])([^"\']*?)(\2)(.*)'
            match = re.match(pattern, line)
        
        if match:
            # Replace the entire URL while keeping the same quote type and everything else
            new_line = f'{match.group(1)}{match.group(2)}{story_data_sheet_URL}{match.group(4)}{match.group(5)}'
            updated_lines.append(new_line)
            variable_found = True
        else:
            updated_lines.append(line)

    return updated_lines if variable_found else lines

def enable_github_page(repo) -> tuple:
    """Enable GitHub Pages for the repository.
    
    Returns a tuple of (result, page, error_message).
        result can be "created", "exists", or "error".  
        page is the page object if the page was created or already exists, otherwise None.
        error_message is the error message if an error occurred, otherwise None.
    """

    try:
        page = get_repo_page(repo)
        if page:
            return "exists", page, None
    
        url = f"https://api.github.com/repos/{repo.full_name}/pages"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "source": {
                "branch": "main",
                "path": "/"
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            return "created", response.json(), None
        else:
            return "error", None, f"Failed to enable Pages: {response.status_code} - {response.text}"
            
    except Exception as e:
        return "error", None, e
    
def get_repo_page(repo):
    url = f"https://api.github.com/repos/{repo.full_name}/pages"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else :
        return None

