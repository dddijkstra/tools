import os

class Config:
    def __init__(self, web_path, time_sleep):
        local_path = os.getcwd()
        self.dir_path = f"{local_path}/"
        self.result_file_path = f"{local_path}/result.txt"
        self.user_data_dir = f"{local_path}/Storage"
        self.web_path = web_path
        self.time_sleep = time_sleep
