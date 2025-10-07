
import os
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


GOOGLE_CREDS = None
SHEETS_SERVICE = None
DRIVE_SERVICE = None
VERBOSE = False

def set_verbose(verbose):
    """Set the global verbose flag"""
    global VERBOSE
    VERBOSE = verbose

def authenticate_google_user() -> None:
    """Authenticate using OAuth2 user credentials"""
    global GOOGLE_CREDS
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 
              'https://www.googleapis.com/auth/drive']
    creds = None
    
    if VERBOSE:
        print("Authenticating Google user...")
    # Token file stores the user's access and refresh tokens
    if os.path.exists('.auth/token.json'):
        if VERBOSE:
            print("Loading existing credentials from .auth/token.json...")
        creds = Credentials.from_authorized_user_file('.auth/token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("No valid credentials found. Opening browser for authentication...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '.auth/credentials.json', SCOPES)  # These are the OAuth2 client secrets
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print("Error: '.auth/credentials.json' file not found. Please ensure it exists.")
                print("Refer to README for instructions on how to set up the credentials file. ")
                exit(1)
            except Exception as e:
                print(f"Could not authenticate with Google using '.auth/credentials.json: {e}")
                print("Refer to README for instructions on how set up Google Authentication. ")
                exit(1)
        
        # Save the credentials for the next run
        with open('.auth/token.json', 'w') as token:
            print("Saving new credentials to .auth/token.json...")
            token.write(creds.to_json())
    print(f"Google user authenticated successfully")
    GOOGLE_CREDS = creds

def ensure_google_setup() -> None:
    """Set up Google Sheets and Drive services using the authenticated credentials."""
    global SHEETS_SERVICE, DRIVE_SERVICE
    try:
        if GOOGLE_CREDS is None:
            authenticate_google_user()

        if GOOGLE_CREDS is None:
            print("Error: Cannot set up Google services: Failed to authenticate with Google")
            print("If your credentials have expired, delete the .auth/token.json file and try again.")
            exit(1)


        if SHEETS_SERVICE is None:
            SHEETS_SERVICE = build("sheets", "v4", credentials=GOOGLE_CREDS)
        if DRIVE_SERVICE is None:
            DRIVE_SERVICE = build("drive", "v3", credentials=GOOGLE_CREDS)
    except Exception as e:
        print(f"Error setting up Google services: {e}")
        print("If your credentials have expired, delete the .auth/token.json file and try again.")
        exit(1)

def sanitize_repo_name(repo_name):
    """
    Convert repo name to contain only alphanumeric characters and dashes.
    Spaces (single or multiple) are converted to single dashes.
    Non-alphanumeric characters (except spaces) are removed.

    returns: A sanitized version of the repo name suitable for GitHub.
    """
    if not repo_name:
        return ""
    
    # Remove non-alphanumeric characters except spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\s\-]', '', repo_name)
    
    # Replace one or more spaces with a single dash
    cleaned = re.sub(r'\s+', '-', cleaned)
    
    # Remove leading/trailing dashes
    cleaned = cleaned.strip('-')
    
    # Convert to lowercase (GitHub convention)
    cleaned = cleaned.lower()
    
    return cleaned

def sanitize_author_name(author_name) -> str:
    """
    Sanitize author names by removing leading/trailing whitespace and converting to title case.

    returns: A sanitized version of the author name.
    """
    if not author_name:
        return ""
    
    # Remove leading/trailing whitespace and convert to title case
    author_name = author_name.strip()
    # Normalize remaining spaces
    author_name = re.sub(r'\s+', ' ', author_name)
    return author_name

def convert_author_names_to_list(author_columns) -> str:
    """Convert columns of author names into a string with commas separating each author.
    
    returns: A string of author names separated by commas.
    """

    author_names = [] 
    
    for column_value in author_columns: 
        sanitized_name = sanitize_author_name(column_value)
        if sanitized_name:
            author_names.append(sanitized_name)

    return ", ".join(author_names)

def convert_sheet_values_to_repo_names_and_authors(sheet_values) -> list:
    """Convert Google Sheet values to a list of repository names.
    
    Returns a list of dictionaries with 'title', 'repo-name', and 'authors' keys.
    """
    converted_data = []
    for row in sheet_values:
        if row:  
            original_name = row[0].strip() if row[0] else "" # First column is the repository name
            repo_name = sanitize_repo_name(row[0])  
            student_names = convert_author_names_to_list(row[1:]) # Subsequent columns are one column per author
    
            repo_data = {
                "title": original_name,
                "repo-name": repo_name,
                "authors": student_names
            }
            converted_data.append(repo_data)
    return converted_data

def fetch_repo_data_from_google_sheet(google_sheet_id) -> list:
    """Fetch repository names and authors from the first sheet of a Google Sheet.

    Returns a list of dictionaries with 'title', 'repo-name', and 'authors' keys.
    """
    if VERBOSE:
        print("Reading repository names from Google Sheet...")
    ensure_google_setup()

    try:

        # Get the first sheet's name, as it is required to get the values for the sheet
        sheet_metadata = SHEETS_SERVICE.spreadsheets().get(spreadsheetId=google_sheet_id).execute()
        first_sheet_name = sheet_metadata['sheets'][0]['properties']['title']

        # Get all the values from the first sheet
        sheet1_values = SHEETS_SERVICE.spreadsheets().values().get(
            spreadsheetId=google_sheet_id,
            range=first_sheet_name
        ).execute()
    except Exception as e:
        print(f"Error reading Google Sheet: {e}")
        print("Ensure the Google Sheet ID is correct and you have access to it.")
        exit(1)
    
    sheet1_values = sheet1_values.get('values', [])
    if not sheet1_values:
        print("No data found in the Google Sheet that is supposed to have repository and author names.")
        return []
    
    # skip the header row and convert the rest
    return convert_sheet_values_to_repo_names_and_authors(sheet1_values[1:])

def get_google_file(folder_id, file_name) -> tuple:
    """Check if a file with the given name exists in the specified Google Drive folder.
    
    Returns a tuple of (file_id, file_url) if the file exists, otherwise (None, None).
    """
    ensure_google_setup()

    try:
        query = f"name='{file_name}' and trashed=false"
        if folder_id:
            query += f" and '{folder_id}' in parents"

        results = DRIVE_SERVICE.files().list(q=query, pageSize=1, fields='files(id,name, webViewLink)').execute()
        items = results.get('files', [])
        if items:
            return items[0]['id'], items[0]['webViewLink']
        else:
            return None, None  # File not found
    except Exception as e:
        return None, None

def copy_story_data_sheet_to_new_sheet(template_sheet_id, batch_sheet_name, batch_sheet_folder_id=None) -> tuple:
    """Copy the source Google Sheet to a new sheet with the specified name.
    
    Returns a tuple of (result, new_sheet_id, new_sheet_URL, error_message).
        result can be "created", "exists", or "error"
        new_sheet_id is the ID of the newly created sheet or None if an error occurred.
        new_sheet_URL is the URL of the newly created sheet or None if an error occurred.
        error_message is the error message if an error occurred, otherwise None.
    """
    ensure_google_setup()

    new_sheet_id, new_sheet_URL = get_google_file(batch_sheet_folder_id, batch_sheet_name)
    if new_sheet_URL:
        return "exists", new_sheet_id, new_sheet_URL, None

    try:
        copy_body_params = {"name": batch_sheet_name}
        if batch_sheet_folder_id:
            copy_body_params["parents"] = [batch_sheet_folder_id]

        copied_sheet = DRIVE_SERVICE.files().copy(
            fileId=template_sheet_id,
            body=copy_body_params
        ).execute()

        new_sheet_id, new_sheet_URL = get_google_file(batch_sheet_folder_id, batch_sheet_name)        
        return "created", new_sheet_id, new_sheet_URL, None
    except Exception as e:
        return "error", None, None, e
    

def share_sheet_with_anyone(sheet_id) -> tuple:
    """Share sheet to anyone with the link.
    
    Returns a tuple of (result, error_message).
        result can be "shared", "already_shared", or "error".
        error_message is the error message if an error occurred, otherwise None.
    """
    ensure_google_setup()

    try:
        if is_sheet_already_shared(sheet_id) :
            return "already_shared", None
        
       # Share with anyone who has the link
        permission = {
            'type': 'anyone',
            'role': 'writer'
        }
        
        DRIVE_SERVICE.permissions().create(
            fileId=sheet_id,
            body=permission
        ).execute()
        
        return "shared", None
        
    except Exception as e:
        return "error", e
    
def is_sheet_already_shared(sheet_id):
    """Is a sheet already shared with anyone with a link?"""

    permissions = DRIVE_SERVICE.permissions().list(fileId=sheet_id).execute()
    for permission in permissions.get('permissions', []):
        if permission.get('type') == 'anyone':
            return True
    return False

def edit_sheet_with_project_info(sheet_id, project_name, authors) -> tuple:
    """Edit the Google Sheet with the project name and authors.
    Returns a tuple of (result, error_message).
        result can be "updated" or "error"
        error_message is the error message if an error occurred, otherwise None.
    """

    try:
        ensure_google_setup()

        # Update the Scrolly Story Title cell
        SHEETS_SERVICE.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="Story!B2",  # The Title of the Scrolly Story
            valueInputOption="RAW", 
            body={
                "values": [[project_name]] 
            }
        ).execute()
        
        # Update the Scrolly Story Authors cell
        SHEETS_SERVICE.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="Story!D2",  # The Authors field
            valueInputOption="RAW",
            body={
                "values": [[authors]]
            }
        ).execute()

        # The update function returns a dict with info on what was updated but
        # we only care unless there's an error, which is caught in the try-except block
        return "updated", None
        
    except Exception as e:
        return "error", e
    