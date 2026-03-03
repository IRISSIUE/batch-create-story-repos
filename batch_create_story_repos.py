import yaml
import os
from datetime import datetime

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

SUMMARY_HTML_FILE = "batch_summary"

def sanitize_sheet_name(sheet_name):
    """Sanitize the sheet name to remove unwanted characters."""
    return ''.join(char for char in sheet_name if char.isalnum() or char.isspace()).strip()

def print_and_verify_repos_with_user(repo_data):
    """Print the repo data to user and verify if they want to proceed."""
    print(f"\n{len(all_repo_data)} projects to be processed from 'input_data_sheet_id' file in the config.yaml:")
    for data in repo_data:
        print(f"      Project: \"{data['title']}\" | Repo: {data['repo-name']} | Students: {data['authors']}")

    print("GitHub repositories and Google data sheets will be created and configured for the projects above, if they do not already exist")

    
    proceed = input("\nDo you want to proceed with creating these repositories? (yes/no): ").strip().lower()
    if proceed != "yes":
        print("Goodbye!")
        exit(0)

def print_processed_repos():
    """Print the processed repositories."""
    print("\n\nProcessed Repositories:")
    for repo in all_processed_repo_URLs:
        print(f"  - {repo['title']}:")
        print(f"      Google Data Sheet URL: {repo['google_sheet_url']}")
        print(f"      GitHub Pages URL: {repo['pages_url']}")
        print(f"      GitHub URL: {repo['github_url']}")


def output_summary_to_html_file(repos):
    """Update or create a local HTML summary file with the processed repositories."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = SUMMARY_HTML_FILE + now.replace(" ", "_").replace(":", "-") + ".html"
    
    # Header
    html_content = f"""
    <div class="batch-run">
        <h2 style="border-bottom: 2px solid #333; padding-top: 20px;">Batch Processed on: {now}</h2>
    """
    
    # Repository details for every processed repository
    for repo in repos:
        html_content += f"""
        <div class="project" style="margin-bottom: 30px; padding: 10px; border: 1px solid #ddd; border-top: 2px solid #333; background-color: #fff;">
            <h3 style="margin: 0 0 5px 0; color: #000; text-decoration: none; border-bottom: 2px solid #eee; padding-bottom: 4px;">{repo['title']}</h3>
            
            <div style="margin: 0; padding: 0; line-height: 1.2;">
                <div style="margin-bottom: 4px; text-decoration: none;">
                    <a href="{repo['google_sheet_url']}" target="_blank" style="color: #1155cc; text-decoration: underline; font-weight: bold;">Google Data Sheet</a>: 
                    <span style="color: #444; font-size: 0.95em; text-decoration: none;">The source data for the story, used to edit content and settings.</span>
                </div>
                
                <div style="margin-bottom: 4px; text-decoration: none;">
                    <a href="{repo['pages_url']}" target="_blank" style="color: #1155cc; text-decoration: underline; font-weight: bold;">Public Story Site</a>: 
                    <span style="color: #444; font-size: 0.95em; text-decoration: none;">The live, published version of the story.</span>
                </div>
                
                <div style="margin-bottom: 4px; text-decoration: none;">
                    <a href="{repo['github_url']}" target="_blank" style="color: #1155cc; text-decoration: underline; font-weight: bold;">GitHub Repository</a>: 
                    <span style="color: #444; font-size: 0.95em; text-decoration: none;">The git repository containing the source code and configuration.</span>
                </div>
            </div>
        </div>
        <br style="text-decoration: none;">
        """
    
    html_content += "</div>"
    

    # Create  file with basic HTML structure
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Batch Creation Summary</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }}
        .batch-run {{ background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Batch Repository Summaries</h1>
    {html_content}
</body>
</html>"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"\n✓ Local summary file created: {SUMMARY_HTML_FILE}")


login_to_github()

all_repo_data = fetch_repo_data_from_google_sheet(INPUT_DATA_SHEET_ID)
print_and_verify_repos_with_user(all_repo_data)

all_processed_repo_URLs = []

for repo_data in all_repo_data:

    print(f"\nProcessing repository: {repo_data['title']}...")
    
    result, new_repo, e = create_repo_from_template(
        template_path=f"{TEMPLATE_REPO_OWNER}/{TEMPLATE_REPO_NAME}",
        batch_repo_owner=BATCH_REPO_OWNER,
        batch_repo_name=f"{BATCH_REPO_NAME_PREFIX}-{repo_data['repo-name']}",    
        batch_repo_description=f"{BATCH_REPO_DESCRIPTION_PREFIX} {repo_data['title']}")
    if result == "error":
        print(f"     ❌ Failed to create GitHub repository for {repo_data['title']}")
        print(f"     Error: {str(e)}")
        print("      Skipping...   ")
        continue
    elif result == "exists":
        print(f"     ✓ GitHub Repository already exists: {new_repo.html_url}")
    elif result == "created":
        print(f"     ✓ GitHub Repository created: {new_repo.archive_url}")


    result, story_data_sheet_id, story_data_sheet_URL, e = copy_story_data_sheet_to_new_sheet(
        template_sheet_id=TEMPLATE_SHEET_ID,
        batch_sheet_name=sanitize_sheet_name(f"{BATCH_SHEET_NAME_PREFIX}{repo_data['title']}"),
        batch_sheet_folder_id=BATCH_SHEET_FOLDER_ID
    )
    if result == "error":
        print(f"     ❌ Failed to create Google data sheet")
        print(f"     Error: {str(e)}")
        print(f"     Skipping...")
        continue
    elif result == "exists":
        print(f"     ✓ Google Data Sheet already exists: {story_data_sheet_URL}")
    elif result == "created":
        print(f"     ✓ Google Data Sheet created: {story_data_sheet_URL}")


    result, e = share_sheet_with_anyone(story_data_sheet_id)
    if result == "error":
        print(f"     ❌ Failed to share data sheet to anyone with link")
        print(f"     Error: {str(e)}")
    elif result == "already_shared":
        print(f"     ✓ Google Data sheet already shared with anyone with link")
    elif result == "shared":
        print(f"     ✓ Google Data sheet shared with anyone with link")


    result, e = edit_sheet_with_project_info(story_data_sheet_id, repo_data['title'], repo_data['authors'])
    if result == "error":
        print(f"     ❌ Failed to update data sheet with story title and authors")
        print(f"     Error: {str(e)}")
    elif result == "updated":
        print(f"     ✓ Google Data Sheet updated with story title and authors")


    result, e = update_repo_with_google_data_sheet_link(
            repo=new_repo,
            story_data_sheet_URL=story_data_sheet_URL,
            file_to_update=BATCH_FILE_NAME_TO_EDIT,
            variable_to_update=BATCH_FILE_VARIABLE_TO_EDIT
    )
    if result == "error":
        print(f"     ❌ Failed to edit {BATCH_FILE_NAME_TO_EDIT} in the repo to point it back to data sheet")
        print(f"     Error: {str(e)}")
    elif result == "no changes":
        print(f"     ✓ GitHub already updated to point to new Google Data Sheet URL for data. Either already up to date or no variable found.")
    elif result == "updated":
        print(f"     ✓ GitHub updated to point to new Google Data Sheet URL for data.")


    result, page, e = enable_github_page(new_repo)
    if result == "error":
        print(f"     ❌ Failed to enable GitHub Page for {new_repo.full_name}")
        print(f"     Error: {str(e)}")
    elif result == "exists":
        print(f"     ✓ GitHub Pages link already enabled: {page['html_url']}")
    elif result == "created":
        print(f"     ✓ Enabled Github Pages link: {page['html_url']}")


    # Add the processed repository info to the list
    repo_info = {
        'title': repo_data['title'],
        'github_url':  new_repo.html_url,
        'google_sheet_url': story_data_sheet_URL,
        'pages_url': page['html_url']
    }
    all_processed_repo_URLs.append(repo_info)

print_processed_repos()
output_summary_to_html_file(all_processed_repo_URLs)

print("\n\nHave a nice day.\n")

exit(0)





