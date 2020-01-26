import os
import json
from utils.ds_path import Path
from utils.GoogleDriveApi import GoogleDrive
import time
import shutil
import logging

logging.basicConfig(filename='log/drive_api.log', filemode='a', format = '%(asctime)s:%(funcName)s:%(levelname)s:%(name)s:%(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
google_drive = GoogleDrive()
_PATH_ = Path("HomeSafety")
_ONE_DAY_IN_SECONDS = 60*60*24
# opens folder_id.json file and loads all id's to python dict
with open("config/folder_id.json", "r") as f:
    _FOLDER_IDS_=json.load(f)

train_data_folder = os.listdir(_PATH_.train_data_dir)
# list to train_data folder. expected result => [train, test]
while True:
    logging.info("Deneme")
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
    break