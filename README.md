
The following package need to be installed to do development

$pip install PyGithub google-api-python-client google-auth google-auth-oauthlib PyYAML

To run:
Update the config.yaml with the parameters to use
Find your GitHub Personal Access Token and set the GITHUB_TOKEN environment variable to it:
    export GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXX (Unix/Linux/macOS)
    set GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXX (Windows)
    $env:GITHUB_TOKEN="ghp_XXXXXXXXXXXXXXXXXX" (Windows PowerShell)
$python story-repo-steup.py

# Google Authorization and Credentials.json
If we want to read a Google Sheet with project and student information (that
is not public) from an
account other than IRISSIUE (which has already been configured), do the following
from that account
1. Go to the account's Google Cloud Console
2. Select this project (or create one if it doesn't exist)
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
    1. After creating the OAuth client ID, click the Download button (download icon)
    2. Save the downloaded file as credentials.json in this project folder (the same directory as the python story-repo-setup.py script)


TODO: API Key is only needed to access public documents. See if we need it when copying the sheet template and editing it

Here's the IRISSIUE credentials screen where you can download the API key
https://console.cloud.google.com/apis/credentials?authuser=3&inv=1&invt=Ab3YAA&project=wide-approach-449221-u6


