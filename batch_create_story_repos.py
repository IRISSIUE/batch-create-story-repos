import yaml

from google_functions import fetch_repo_data_from_google_sheet
from google_functions import copy_story_data_sheet_to_new_sheet
from google_functions import share_sheet_with_anyone
from google_functions import edit_sheet_with_project_info

from github_functions import login_to_github
from github_functions import create_repo_from_template
from github_functions import update_repo_with_google_data_sheet_link
from github_functions import enable_github_page


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
BATCH_FILE_NAME_TO_EDIT = gh_config["batch_file_name_to_edit_with_new_story_sheet_id"]
BATCH_FILE_VARIABLE_TO_EDIT = gh_config["batch_file_variable_to_edit_with_new_data_sheet_id"]

# Google config
g_config = config["google"]
INPUT_DATA_SHEET_ID = g_config["input_data_sheet_id"]
TEMPLATE_SHEET_ID = g_config["template_sheet_id"]
BATCH_SHEET_NAME_PREFIX = g_config["batch_sheet_name_prefix"]
BATCH_SHEET_FOLDER_ID = g_config.get("batch_sheet_folder_id", None)

login_to_github()

all_repo_data = fetch_repo_data_from_google_sheet(INPUT_DATA_SHEET_ID)
print(f"Fetched {len(all_repo_data)} repository names from Google Sheet.")
print(all_repo_data)

for repo_data in all_repo_data:

    print(f"Processing repository: {repo_data['title']}...")
    
    result, new_repo = create_repo_from_template(
        template_path=f"{TEMPLATE_REPO_OWNER}/{TEMPLATE_REPO_NAME}",
        batch_repo_owner=BATCH_REPO_OWNER,
        batch_repo_name=f"{BATCH_REPO_NAME_PREFIX}-{repo_data['repo-name']}",    
        batch_repo_description=f"{BATCH_REPO_DESCRIPTION_PREFIX} {repo_data['title']}")
    if result == "error":
        print(f"     ❌ Failed to create repository for {repo_data['title']}. Skipping...")
        continue
    elif result == "exists":
        print(f"     ✓ GitHub Repository already exists: {new_repo.html_url}")
    elif result == "created":
        print(f"     ✓ GitHub Repository created: {new_repo.archive_url}")


    result, story_data_sheet_id, story_data_sheet_URL = copy_story_data_sheet_to_new_sheet(
        template_sheet_id=TEMPLATE_SHEET_ID,
        batch_sheet_name=f"{BATCH_SHEET_NAME_PREFIX}{repo_data['title']}",
        batch_sheet_folder_id=BATCH_SHEET_FOLDER_ID
    )
    if result == "error":
        print(f"     ❌ Failed to create Google data sheet")
        print(f"     Error: {story_data_sheet_URL}")
        print(f"     Skipping...")
        continue
    elif result == "exists":
        print(f"     ✓ Google Data Sheet already exists: {story_data_sheet_URL}")
    elif result == "created":
        print(f"     ✓ Google Data Sheet created: {story_data_sheet_URL}")


    result, e = share_sheet_with_anyone(story_data_sheet_id)
    if result == "error":
        print(f"     ❌ Failed to publish sheet to web")
        print(f"     Error: {e}")
    elif result == "already_shared":
        print(f"     ✓ Already shared with anyone with link: {story_data_sheet_URL}")
    elif result == "updated":
        print(f"     ✓ Shared with anyone with link: {story_data_sheet_URL}")


    result, e = edit_sheet_with_project_info(story_data_sheet_id, repo_data['title'], repo_data['authors'])
    if result == "error":
        print(f"     ❌ Failed to edit {story_data_sheet_URL} with story title and authors")
        print(f"     Error: {e}")
    elif result == "updated":
        print(f"     ✓ Updated {story_data_sheet_URL} with story title and authors")


    result, e = update_repo_with_google_data_sheet_link(
            repo=new_repo,
            story_data_sheet_URL=story_data_sheet_URL,
            file_to_update=BATCH_FILE_NAME_TO_EDIT,
            variable_to_update=BATCH_FILE_VARIABLE_TO_EDIT
    )
    if result == "error":
        print(f"     ❌ Failed to edit {BATCH_FILE_NAME_TO_EDIT} in the repo to point it back to data sheet")
        print(f"     Error: {e}")
    elif result == "no changes":
        print(f"     ✓ No changes made to {BATCH_FILE_VARIABLE_TO_EDIT} var in {BATCH_FILE_NAME_TO_EDIT}. Either already up to date or no variable found.")
    elif result == "updated":
        print(f"     ✓ Updated {BATCH_FILE_NAME_TO_EDIT} with new Data Google Sheet URL.")


    result, page = enable_github_page(new_repo)
    if result == "error":
        print(f"     ❌ Failed to enable GitHub Page for {new_repo.full_name}")
        print(f"     Error: {page}")
    elif result == "exists":
        print(f"     ✓ GitHub page already enabled: {page['html_url']}")
    elif result == "created":
        print(f"     ✓ Enabled Github Pages link: {page['html_url']}")



exit(0)





