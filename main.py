import os
import argparse
import hashlib
import shutil
import time

from logger import Logger


def CreateFolder(destinationPath, logger):
    try:
        os.makedirs(destinationPath)
        logger.CreateDirectory(destinationPath)
    except Exception as e:
        logger.Error(f"An unexpected error appeared when creating a directory {destinationPath}")
        logger.Error(f"{e}")

def ModifyFile(sourcePath, destinationPath, file, logger):
    try:
        wholeSourcePath = str(os.path.join(sourcePath, file))
        wholeDestinationPath = str(os.path.join(destinationPath, file))
        shutil.copy(wholeSourcePath, wholeDestinationPath)
        logger.ModifyFile(wholeDestinationPath)
    except Exception as e:
        logger.Error(f"An unexpected error appeared on file modification {file}")
        logger.Error(f"{e}")

def CreateFile(sourcePath, destinationPath, file, logger):
    try:
        wholeSourcePath = str(os.path.join(sourcePath, file))
        wholeDestinationPath = str(os.path.join(destinationPath, file))
        shutil.copy(wholeSourcePath, wholeDestinationPath)
        logger.CreateFile(wholeDestinationPath)
    except Exception as e:
        logger.Error(f"An unexpected error appeared for file creation {file}")
        logger.Error(f"{e}")

def RemoveFile(path, file, logger):
    try:
        wholePath = os.path.join(path, file)
        os.remove(wholePath)
        logger.DeleteFile(wholePath)
    except Exception as e:
        logger.Error(f"An unexpected error appeared for file removal {file}")
        logger.Error(f"{e}")

def RemoveDirectory(path, dir, logger):
    try:
        wholePath = os.path.join(path, dir)
        shutil.rmtree(wholePath)
        logger.DeleteDirectory(wholePath)
    except Exception as e:
        logger.Error(f"An unexpected error appeared for directory removal {dir}")
        logger.Error(f"{e}")

def GetMD5(path):
    if(os.path.isdir(path)):
        return -1
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

#Returns dictionary with file/dir names as keys and md5sum as values (-1 if dir)
def GetContent(path):
    content = {}
    if os.path.isdir(path):
        keys = os.listdir(path)
        for key in keys:
            content[key] = GetMD5(os.path.join(path, key))
    return content

def SynchronizeDirectories(resourcePath, destinationPath, logger, modified=False):
    #If destination folder doesn't exist create it
    if not os.path.isdir(destinationPath):
        CreateFolder(destinationPath, logger)

    resource = GetContent(resourcePath)
    destination = GetContent(destinationPath)

    #Save it in list so we can remove keys, which we don't need to update
    keysForUpdate = list(resource.keys())
    #Save it in list so check can be faster because we won't check deleted files
    destinationKeys = list(destination.keys())

    #Same files
    for key in resource.keys():
        if resource[key] != -1 and key in destinationKeys and resource[key] == destination[key]:
            #The file doesn't need update so remove it from the update list
            keysForUpdate.remove(key)
            destinationKeys.remove(key)

    #Files only in backup dir
    for key in destinationKeys:
        # File/dir was not found in the list of all resource files
        if key not in keysForUpdate:
            #Dir
            if os.path.isdir(os.path.join(destinationPath, key)):
                RemoveDirectory(destinationPath, key, logger)
            #File
            else:
                RemoveFile(destinationPath, key, logger)
                destinationKeys.remove(key)

    #Create or modify files/dirs
    for key in keysForUpdate:
        #If is dir synchronizeDir
        if resource[key] == -1:
            SynchronizeDirectories(os.path.join(resourcePath, key), os.path.join(destinationPath, key), logger)
        #Is file
        else:
            #Modify existing file
            if key in destinationKeys:
                ModifyFile(resourcePath, destinationPath, key, logger)
            #File doesn't exist, so create it
            else:
                CreateFile(resourcePath, destinationPath, key, logger)


def ParseArguments():
    parser = argparse.ArgumentParser(description="Backup and sync utility")
    parser.add_argument('--log-file', type=str, required=True, help="Path to the log file", dest='logFile')
    parser.add_argument('--resource-folder', type=str, required=True, help="Path to the resource folder", dest='resourceFolder')
    parser.add_argument('--backup-folder', type=str, required=True, help="Path to the backup folder", dest='backupFolder')
    parser.add_argument('--sync-interval', type=int, required=True, help="Interval (in seconds) for synchronization", dest='syncInterval')
    args = parser.parse_args()

    #Check args
    if not os.path.isdir(args.resourceFolder):
        raise ValueError(f"Resource folder doesn't exist: {args.resourceFolder}")

    if not os.path.isdir(args.backupFolder):
        raise ValueError(f"Backup folder doesn't exist: {args.backupFolder}")

    return args

if __name__ == '__main__':
    args = ParseArguments()
    logger = Logger(args.logFile)
    logger.LogInfo("Program started successfully with arguments:")
    logger.LogInfo(f"Logfile: {args.logFile}")
    logger.LogInfo(f"Resource Folder: {args.resourceFolder}")
    logger.LogInfo(f"Backup Folder: {args.backupFolder}")
    logger.LogInfo(f"Sync Interval: {args.syncInterval} seconds")

    #Never ending loop
    while True:
        logger.LogInfo("Synchronization started")
        SynchronizeDirectories(args.resourceFolder, args.backupFolder, logger)
        logger.LogInfo("Synchronization completed")
        logger.LogInfo(f"Sleeping for {args.syncInterval} seconds")
        time.sleep(args.syncInterval)