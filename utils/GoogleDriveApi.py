import pickle
import os.path
from googleapiclient.discovery import build, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from googleapiclient.http import MediaIoBaseDownload
import logging
import sys


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

    # returns file or folder info by given 'name' arg
    def get_info(self, file_name):
        service = self.create_service()
        
        folder = service.files().list(
            q=f"name='{file_name}' and mimeType='application/vnd.google-apps.folder'",
            fields='files(id, name, parents)'
             ).execute()
        
        paths = [self.get_full_path(service,file) for file in folder["files"]]
        return {"info": folder["files"], "paths": paths}
    
    # returns specific folder id by given folder_name args
    
    def get_folder_id(self, folder_name):
        service = self.create_service()

        folder = service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
            fields='files(id)'
        ).execute()

        return folder["files"][0]["id"]
    
    # list the folder by given folder_id args
    def list_folder(self, folder_id):
        service = self.create_service()
        
        result = []
        files = service.files().list(
            pageSize='1000',
            q=f"'{folder_id}' in parents",
            fields='files(id, name, mimeType)').execute()
        result.extend(files['files'])
        
        return result
    
    # download folder from drive by folder_id args
    def download_folder(self, folder_name, folder_id, download_location):
        items = self.list_folder(folder_id)
        download_path = os.path.join(download_location, folder_name)

        if not os.path.exists(download_path):
            print("downloading", folder_name, "to ", download_location)
            os.makedirs(download_path)
            for item in items:
                item_id = item["id"]
                item_name = item["name"]
                mime_type = item["mimeType"]
                print("downloading", item_name, item_id, mime_type)
                if mime_type == 'application/vnd.google-apps.folder':
                    self.download_folder(folder_name = item_name, folder_id= item_id, download_location=download_path)
                else:
                    self.download_file(file_name = item_name, file_id= item_id, download_location=download_path)
        else:
            print("already exist")

    #  dowload file from drive by file_id args
    def download_file(self, file_name, file_id, download_location):
        service = self.create_service()
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(os.path.join(download_location, file_name), 'wb')
        downloader = MediaIoBaseDownload(fh, request, 1024 * 1024 * 1024)
        done = False
        while not done:
            try:
                status, done = downloader.next_chunk()
            except:
                logger.error("Error while downloading file")
    def get_full_path(self, service, folder):
        if not 'parents' in folder:
            return folder['name']
        files = service.files().get(fileId=folder['parents'][0], fields='id, name, parents').execute()
        path = files['name'] + '/' + folder['name']
        while 'parents' in files:
            files = service.files().get(fileId=files['parents'][0], fields='id, name, parents').execute()
            path = files['name'] + '/' + path
        return path