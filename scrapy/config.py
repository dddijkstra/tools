import os

class Config:
    def __init__(self, result_file, user_data, web_path, time_sleep):
        local_path = os.getcwd()
        self.dir_path = f"{local_path}/"
        self.result_file_path = f"{local_path}/{result_file}"
        self.user_data_dir = f"{local_path}/{user_data}"
        self.web_path = web_path
        self.time_sleep = time_sleep
