import pickle
import os.path
from googleapiclient.discovery import build, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import logging



# path declerations
_CURRENT_PATH_ = os.path.dirname(os.path.abspath(__file__))
_TOKEN_PATH_ = os.path.join(_CURRENT_PATH_, "token.pickle")
_CREDENTIALS_PATH_ = os.path.join(_CURRENT_PATH_, "credentials.json")
_LOG_PATH_ = os.path.join(_CURRENT_PATH_.replace("utils", "log"), "drive_api.log")
logging.basicConfig(filename=_LOG_PATH_, filemode='a', format = '%(asctime)s:%(funcName)s:%(levelname)s:%(name)s:%(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# this scope for drive create delete 
# if you change the scope delete the token.pickle file
SCOPES = ['https://www.googleapis.com/auth/drive']

class GoogleDrive():
    def __init__(self):
        self.creds = None
        
    def create_service(self):
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        try:
            if os.path.exists(_TOKEN_PATH_):
                with open(_TOKEN_PATH_, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in.
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        _CREDENTIALS_PATH_, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(_TOKEN_PATH_, 'wb') as token:
                    pickle.dump(self.creds, token)
        except Exception as err:
            logging.error(err)
            raise(err)
        
        return build('drive', 'v3', credentials=self.creds)

    def upload(self, name, file_path, parent_folder, mimetype):
        service = self.create_service()
        #  set file options such as name and parent directory
        #  this folder id is for `train` folder
        file_metadata = {'name': name, "parents": parent_folder}
        #  file type. this mimetype is for image/jpeg
        media = MediaFileUpload(file_path, mimetype=mimetype)
        # upload to drive with service
        try:
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        except Exception as err:
            logging.error(err)
            raise(err)
        return file