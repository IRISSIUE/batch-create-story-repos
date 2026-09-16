# Overview
This script reads a list of project names and students from a spreadsheet
and batch creates/configures GitHub repositories and Google Data Sheets copied from a template, which is a general way of saying that it sets up a class of student to use one of:
* The Scrolly Story Generator
* Leaflet StoryMaps

both of which work by copying their GitHub repositories and a sample google 
sheets, one per project, to a place where the students can easily access them.

## Configuring the script
The script requires a lot of configuration before being run:
1. **Config.yaml**. Most input variables are specified in the config.yaml file that is included in the project. The variables here control what is copied and how to configure the projects for use in a classroom by students. The yaml file explains what each parameter does, and has a variable for where to find the Input Google Sheet (below).
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

## Permissions

In order to create the google data sheets required by a Scrolly or Leaflet Story, this script needs permission to
create those sheets the google drive specified in your configuration parameters.

In the case of SIUE CODES students, this is the IRISSIUE google account, which has folders organized in [its Google Drive](https://drive.google.com/drive/u/3/my-drive) that contain the data sheets. You'll need the IRISSIUE password to generate these. When you run the script, you'll be asked to login to IRISSIUE.

The first time you run this script, you'll also need a "credentials.json" file to be put in the ./auth folder with this script's OAuth2 credentials (see below). It can't be put into the github repository for security reasons, but is available in the [OAuth2 Credentials folder](https://drive.google.com/drive/u/3/folders/1u8vY4bKWRXkjyQRdfg5XNqWjJEizs13W) of the IRISSIUE google drive. See below if the file is lost and you need to generate a new one.  

**OAuth2** 

 This project uses OAuth2 authentication to get permissions to create Google sheets in the account it is directed to. OAuth2 allows an app to login to Google from the app without the app knowing what the username/password is (all the authentication is handled by Google, without the app knowing anything about passwords). 
 
 OAuth2 requires information from a credentials.json file from google that identifies this script/app as a valid application, even before it asks you for your Google account and password.
 
 If you're not running the script for the SIUE CODEs program, you'll have to create this credentials file in Google and place it in the ./auth folder of this project. Once you create it, you won't have to worry about it again, unless you lose the credentials.json file or the permissions need to change for some reason. Then you'll have to recreate it. 

 Make sure the google account you are using has access to the Input Google Sheet and the template Google Data Sheet this project is copying, as well as access to the parent folder in which you plan to create the Google Data Sheets.

For Google OAuth2, you create a credentials.json file from the Google Cloud Console: 

1. Go to https://console.cloud.google.com
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

**Login Token**

When you login using OAuth2 (logging in via Google), it will create a "token.json" file and put it in the ./auth folder of this project. This saves your login information (not your password, but a token) for a limited amount of time that allows you to run the script again without having to login in again.

This token eventually expires, and if so, you'll get a message to delete the token.json file, the only side effect of doing so is that you'll have to login again. 

##TO DO

* Verbose Mode
* Batch Summary File Creation
* Default Configurations for each project type

## Running the Script

1. Update your Python dependencies to include packages this script uses
```bash
pip install PyGithub google-api-python-client google-auth google-auth-oauthlib PyYAML
```
2. Run the script
```bash
 py .\batch_create_story_repos.py
```

