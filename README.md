# Overview
This script batch creates and configures a number of GitHub repositories and Google Data Sheets copied from a template GitHub Repository. 

It currently works for the Scrolly Story Generator template but will eventually be expanded to also work for Leaflet StoryMaps and others.

## Configuring the script
The script requires a lot of configuration before being run:
1. **Config.yaml**. Most input variables are specified in the config.yaml file that is included in the project. The file explains what each parameter does, as well as the format of the Input Google sheet.
2. **The Input Google Sheet**. You need to create a spreadsheet of input data that contains every project name plus the students assigned to the project. This script creates a GitHub Repository and Google Data Sheet for each, customized to work for that project. Note that the (script) Google Input Sheet is different from the (project) Google Data Sheet. There is one Google Input sheet containing all the project names, and one Google Data Sheet created for each project in the input sheet.
3. **GitHub Token**. In order to create and modify a GitHub repository, you need to provide your GitHub Personal Access Token. For security reasons, this should never be stored in a .yaml file or input as a command line argument, so you'll have to set it as an environment variable for the script to read. Use one of the following commands to do this before running the script:
Set your GitHub Personal Access Token as an environment variable:
```bash
# Windows Command Prompt
set GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXX

# Windows PowerShell  
$env:GITHUB_TOKEN="ghp_XXXXXXXXXXXXXXXXXX"

# Unix/Linux/macOS
export GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXX
```

4. **OAuth2** This project uses OAuth2 authentication to gain access to the Google sheets (for reading the input and creating data sheets). This means that the first time you run the script, you'll login into a google account (that has permissions to the files you are accessing) from your web browser. After that, the credentials will be saved locally and you shouldn't have to login again, unless the permissions need to change for additional functionality added later. 

    For OAuth2, you need to create a credentials.json file from the Google Cloud Console, and place it in the /.auth folder of this project. The credentials.json file contains the identity of this script (app) so that OAuth can ensure you have the right permissions.

    The IRISSIUE google account is already partially setup to handle this, in that it already has a "Batch Create and Configure Story Repos" OAuth2 client defined. However, you need to create a custom secrets file for yourself from there. If you have access to IRISIUE:
    - Go to https://console.cloud.google.com/apis/credentials?inv=1&invt=Ab4KJA&authuser=3&project=wide-approach-449221-u6
    - Click on the "Batch Create and Configure Story Repos" OAuth2 client
    - Click on the "+ Add secret" button on the bottom right of that page
    - In the bottom right of that screen, there should now be a new client secret with a download button next to it. Click the download button to download a json file. NOTE: It can only be downloaded once, so if you lose it, you'll have to delete this secret and create a new credentials.json file
    - Rename the downloaded .json file (will be client_secret_yadda_yadda.json) to "credentials.json"
    - Move credentials.json to the ./auth folder in this project

If you are using a different google account:
1. Make sure the google account has access to the Input Google Sheet and the template Google Data Sheet that will be used to copy, as well as access to the parent folder in which you plan to create the Google Data Sheets.
2. Create a new Project/App
3. Enable the Google Sheets API:
    - Go to APIs & Services -> Library
    - Search for "Google Sheets API" and enable it
4. Create OAuth2 credentials:
    - Go to APIs & Services -> Credentials
    - Click Create Credentials -> OAuth client ID
    - Choose Desktop application
    - Give it a name (e.g., "Story Repo Setup Script")
    - Click Create
5. Download the credentials.json file
    - After creating the OAuth client ID, click the Download button (download icon)
    - Save the downloaded file as credentials.json in this project folder 

## Running the Script

1. Update your Python dependencies for packages this script uses
```bash
pip install PyGithub google-api-python-client google-auth google-auth-oauthlib PyYAML
```
2. Run the script
```bash
 py .\batch_create_story_repos.py
```

