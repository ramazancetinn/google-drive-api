import os
from typing import List

class Path():
    def __init__(self, class_name):
        self.class_name = class_name
    @property
    def cls_dir(self) -> str:
        return os.path.join(os.getenv("HOME"), "hs", "projects", self.class_name)
    @property
    def train_data_dir(self) -> str:
        return os.path.join(self.cls_dir, 'data', 'train_data')
    @property
    def drive_uploaded(self) -> str:
        return os.path.join(self.cls_dir, "data", "drive_uploaded")

