import os
import logging

class Logger:
    def __init__(self, logFile):
        self.logFile = logFile
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.DEBUG)

        fileHandler = logging.FileHandler(logFile, encoding='utf-8')
        fileHandler.setLevel(logging.DEBUG)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        consoleHandler.setFormatter(formatter)
        fileHandler.setFormatter(formatter)

        consoleHandler.stream.reconfigure(encoding='utf-8')

        self.log.addHandler(consoleHandler)
        self.log.addHandler(fileHandler)

        os.makedirs(os.path.dirname(logFile), exist_ok=True)

    def LogInfo(self, message):
        self.log.info(message)

    def DeleteFile(self, file):
        self.log.info(f"File {file} was deleted")

    def CreateFile(self, file):
        self.log.info(f"File {file} was created")

    def ModifyFile(self, file):
        self.log.info(f"File {file} was modified")

    def CreateDirectory(self, dir):
        self.log.info(f"Directory {dir} was created")

    def DeleteDirectory(self, dir):
        self.log.info(f"Directory {dir} was removed")

    def Error(self, message):
        self.log.error(message)