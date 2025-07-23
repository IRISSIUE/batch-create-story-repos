import yaml


from google_functions import fetch_repo_data_from_google_sheet
from github_functions import login_to_github
from github_functions import create_repo_from_template


# --- Load config from YAML ---
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# GitHub config
gh_config = config["github"]

TEMPLATE_REPO_OWNER = gh_config["template_repo_owner"]
TEMPLATE_REPO_NAME = gh_config["template_repo_name"]
BATCH_REPO_OWNER = gh_config["batch_repo_owner"]
BATCH_REPO_NAME_PREFIX = gh_config["batch_repo_name_prefix"]
BATCH_REPO_DESCRIPTION_PREFIX = gh_config["batch_repo_description_prefix"]

# Google config
g_config = config["google"]
INPUT_DATA_SHEET_ID = g_config["input_data_sheet_id"]
BATCH_SHEET_NAME_PREFIX = g_config["batch_sheet_name_prefix"]


login_to_github()

repo_data = fetch_repo_data_from_google_sheet(INPUT_DATA_SHEET_ID)
print(f"Fetched {len(repo_data)} repository names from Google Sheet.")
print(repo_data)

for repo in repo_data:
    new_repo = create_repo_from_template(
        template_path=f"{TEMPLATE_REPO_OWNER}/{TEMPLATE_REPO_NAME}",
        batch_repo_owner=BATCH_REPO_OWNER,
        batch_repo_name=f"{BATCH_REPO_NAME_PREFIX}-{repo['repo-name']}",    
        batch_repo_description=f"{BATCH_REPO_DESCRIPTION_PREFIX} {repo['name']}")
    if not new_repo:
        print(f"Failed to create repository for {repo['name']}. Skipping...")
        continue



exit(0)  # Exit after reading repo names





