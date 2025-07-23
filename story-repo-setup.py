import yaml


from google_functions import fetch_repo_data_from_google_sheet
from github_functions import login_to_github
from github_functions import create_repo_from_template


# --- Load config from YAML ---
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# GitHub config
gh_config = config["github"]


#GITHUB_TOKEN = gh_config["token_env"]  # For testing, hardcoded token
TEMPLATE_REPO_OWNER = gh_config["template_repo_owner"]
TEMPLATE_REPO_NAME = gh_config["template_repo_name"]
NEW_REPO_OWNER = gh_config["new_repo_owner"]
NEW_REPO_NAME_PREFIX = gh_config["new_repo_name_prefix"]
NEW_REPO_DESCRIPTION_PREFIX = gh_config["new_repo_description_prefix"]

# Google config
g_config = config["google"]
SOURCE_SHEET_ID = g_config["source_sheet_id"]
NEW_SHEET_NAME = g_config["new_sheet_name"]


login_to_github()

repo_data = fetch_repo_data_from_google_sheet(SOURCE_SHEET_ID)
print(f"Fetched {len(repo_data)} repository names from Google Sheet.")
print(repo_data)

for repo in repo_data:
    new_repo = create_repo_from_template(
        template_path=f"{TEMPLATE_REPO_OWNER}/{TEMPLATE_REPO_NAME}",
        new_repo_owner=NEW_REPO_OWNER,
        new_repo_name=f"{NEW_REPO_NAME_PREFIX}-{repo['repo-name']}",    
        new_repo_description=f"{NEW_REPO_DESCRIPTION_PREFIX} {repo['name']}")
    if not new_repo:
        print(f"Failed to create repository for {repo['name']}. Skipping...")
        continue



exit(0)  # Exit after reading repo names





