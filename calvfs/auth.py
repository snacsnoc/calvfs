import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def authenticate_google_calendar():
    creds = None
    # Check for existing saved credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Refresh or re-authenticate if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Ensure the scope here matches your needs for the Calendar API
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            creds = flow.run_local_server(port=0)
        # Save the new credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def deauthenticate():
    # Remove saved credentials to force re-authentication next time
    if os.path.exists('token.pickle'):
        os.remove('token.pickle')
        print("Authentication token removed.")
    else:
        print("No token to remove.")
