import os
import json
from utils.ds_path import Path
from utils.GoogleDriveApi import GoogleDrive
import time
import shutil
import logging
from threading import Thread


_CURRENT_PATH_ = os.path.dirname(os.path.abspath(__file__))
_LOG_PATH_ = os.path.join(_CURRENT_PATH_, "log", "drive_api.log")

logging.basicConfig(filename=_LOG_PATH_, filemode='a', level=logging.INFO, format = '%(asctime)s:%(funcName)s:%(levelname)s:%(name)s:%(message)s')

logger = logging.getLogger()
google_drive = GoogleDrive()
_PATH_ = Path("HomeSafety")
_ONE_DAY_IN_SECONDS = 60*60*24

def upload_drive():
    # opens folder_id.json file and loads all id's to python dict
    with open("config/folder_id.json", "r") as f:
        _FOLDER_IDS_=json.load(f)

    train_data_folder = os.listdir(_PATH_.train_data_dir)
    while True:
        print("Starting system...")
        for parent_folder in train_data_folder:
            for sub_folder in _FOLDER_IDS_[parent_folder]:
                drive_parent_folder = [_FOLDER_IDS_[parent_folder][sub_folder]]
                #  files in sub folder of train and test folder
                #  sub_folder => [not_danger, no_light, danger...]
                files = os.listdir(os.path.join(_PATH_.train_data_dir,parent_folder,sub_folder))
                if files:
                    for file in files:
                        file_path = os.path.join(_PATH_.train_data_dir, parent_folder, sub_folder, file)
                        # uploading to google drive
                        logging.info("Uploading [%s] to drive.... " % file)
                        res = google_drive.upload(name=file, file_path=file_path, parent_folder=drive_parent_folder, mimetype="image/jpeg")
                        logging.info("[%s] Uploaded to drive" % file)
                        #  move file after upload to drive_uploaded folder
                        origin_path = os.path.join(_PATH_.train_data_dir, parent_folder, sub_folder, file)
                        destination_path = os.path.join(_PATH_.drive_uploaded, parent_folder, sub_folder, file)
                        shutil.move(origin_path, destination_path)
        logging.info("Sleeping ONE DAY")
        time.sleep(_ONE_DAY_IN_SECONDS)
def download_drive():
    while True:
        model_versions = google_drive.list_folder(google_drive.get_folder_id("versions"))
        for model in model_versions:
            google_drive.download_folder(folder_name=model["name"], folder_id=model["id"], download_location=_PATH_.trained_model_dir)
        time.sleep(_ONE_DAY_IN_SECONDS)
    
if __name__ == "__main__":
    try:
        Thread(target=upload_drive).start()
        Thread(target=download_drive).start()
    except Exception as e:
        logger.error("Error while trying to start google drive service... %s" % e)