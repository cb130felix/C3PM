import json
import shutil
import os
from os import walk
from os.path import basename
from datetime import datetime
import zipfile
import glob
from contextlib import contextmanager
import re
import logging

# set logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler =  logging.FileHandler('log.txt')
file_handler.setFormatter(formatter)

console = logging.StreamHandler()

logger.addHandler(file_handler)
logger.addHandler(console)

#---------------------------------------------------------

class C3File:

    def __init__(self, name, content, fType, fDir):
        self.name = name
        self.content = content
        self.type = fType
        self.dir = fDir

class C3Project:

    
    c3FileList = []
    
    def __init__(self, path=None):
        
        self.tempPath = os.path.join('temp', str(hash(path)))
        self.sid = 1000000
        self.uid = 1000
        self.pFiles = {
            'c3proj' : {},
            'files' : {
                    'eventSheets' : {'fList' : [], 'subfolders' : [], 'folderName' : 'eventSheets', 'supported' : True, 'metaData' : True, 'c3File' : True},
                    'families' : {'fList' : [], 'subfolders' : [], 'folderName' : 'families', 'supported' : True, 'metaData' : True, 'c3File' : True},
                    'objectTypes' : {'fList' : [], 'subfolders' : [], 'folderName' : 'objectTypes', 'supported' : True, 'metaData' : True, 'c3File' : True},
                    'layouts' : {'fList' : [], 'subfolders' : [], 'folderName' : 'layouts', 'supported' : True, 'metaData' : True, 'c3File' : True},
                    'video' : {'fList' : [], 'subfolders' : [], 'folderName' : 'videos', 'supported' : True, 'metaData' : True, 'c3File' : False},
                    'timelines' : {'fList' : [], 'subfolders' : [], 'folderName' : 'timelines', 'supported' : False, 'metaData' : True, 'c3File' : True},
                    'ease' : {'fList' : [], 'subfolders' : [], 'folderName' : 'timelines/transitions', 'supported' : False, 'metaData' : False, 'c3File' : True},
                    'sound' : {'fList' : [], 'subfolders' : [], 'folderName' : 'sounds', 'supported' : True, 'metaData' : True, 'c3File' : False},
                    'music' : {'fList' : [], 'subfolders' : [], 'folderName' : 'music', 'supported' : True, 'metaData' : True, 'c3File' : False},
                    'general' : {'fList' : [], 'subfolders' : [], 'folderName' : 'files', 'supported' : True, 'metaData' : True, 'c3File' : False},
                    'script' : {'fList' : [], 'subfolders' : [], 'folderName' : 'scripts', 'supported' : True, 'metaData' : True, 'c3File' : False},
                    'images' : {'fList' : [], 'subfolders' : [], 'folderName' : 'images', 'supported' : True, 'metaData' : False, 'c3File' : False},
                    'icon' : {'fList' : [], 'subfolders' : [], 'folderName' : 'icons', 'supported' : True, 'metaData' : False, 'c3File' : False},
                    'font' : {'fList' : [], 'subfolders' : [], 'folderName' : 'fonts', 'supported' : True, 'metaData' : True, 'c3File' : False}
            }
        }

        for fKey, fValue in self.pFiles['files'].items():
            if fValue['c3File']:    
                self.c3FileList.append(fKey)
        
        if not path == None: 
            self.loadProject(path)
        

    def loadProject(self, project_path=''):

        projectName = os.path.basename(project_path.split('.')[0] + str(hash(self)))
        
        logger.info("Loading files... ")
        if (os.path.exists(self.tempPath)):
            shutil.rmtree(self.tempPath)

        
        if project_path.endswith('.c3proj'):
            project_path = os.path.dirname(project_path)
            shutil.copytree(project_path, self.tempPath)
        else:
            with zipfile.ZipFile(project_path, 'r') as zip_ref:
                zip_ref.extractall(self.tempPath)

        logger.info("Loading c3proj file")
        with open(os.path.join(self.tempPath, 'project.c3proj')) as json_file:
            self.pFiles['c3proj'] = json.load(json_file)

        for fileKey, fileValue in self.pFiles['files'].items():

            logger.info("Loading <" + fileKey + "> files...")
            c3Folder = None

            if self.pFiles['files'][fileKey]['metaData']:
                if self.pFiles['files'][fileKey]['supported']:
                    
                    
                    if fileValue['c3File']:
                        c3Folder = self.pFiles['c3proj'][fileKey]
                    else:
                        c3Folder = self.pFiles['c3proj']['rootFileFolders'][fileKey]
            
                    self.loadFiles(fileKey, c3Folder, [])

            else:

                folderPath = os.path.join(self.tempPath, fileValue['folderName'])
                if os.path.exists(folderPath):
                    for fileName in os.listdir(folderPath):

                        fullPath = os.path.join(folderPath, fileName)
                        fileContent = None
                        with open(fullPath, 'rb') as file:
                            fileContent = file.read()

                        c3_file = C3File(fileName, fileContent, None, [])

                        fileValue['fList'].append(c3_file)
                

            if (not fileValue['supported']) and len(fileValue['fList']) > 0:
                raise NameError("Projects with the <" + fileKey + "> file type are not supported")

        shutil.rmtree(self.tempPath)

    def loadFiles(self, fileType, c3Folder, c3Dir):
        
        if 'name' in c3Folder:
            c3Dir.append(c3Folder['name'])

        for item in c3Folder['items']:
            c3_file = None
            dirName = self.pFiles['files'][fileType]['folderName']
            

            if fileType in self.c3FileList:
                tempName = item.lower() + '.json'
                logger.info('file name: ' + tempName)
                with open(os.path.join(self.tempPath, dirName, tempName), encoding='utf8') as json_file:
                    tempJson = json.load(json_file)
                
                c3_file = C3File(tempName, tempJson, None, c3Dir)

            else:
                tempName = item['name']
                tempType = item['type']
                with open(os.path.join(self.tempPath, dirName, tempName), 'rb') as file:
                    tempJson = file.read()

                c3_file = C3File(tempName, tempJson, tempType, c3Dir)

            self.pFiles['files'][fileType]['fList'].append(c3_file)

        for folder in c3Folder['subfolders']:
            
            self.loadFiles(fileType, folder, c3Dir.copy())

        self.pFiles['files'][fileType]['subfolders'].append(c3Dir)
        #logger.info(c3Dir)   
        c3Dir = []
   
    def exportProject(self, export_path='export', name='c3project', one_file=True):
       
        logger.info("Exporting files...")
        
        #creating main folder and c3proj file
        if  not os.path.exists(self.tempPath):
            os.makedirs(self.tempPath)
        
        #updating c3proj file
        self.updateC3proj()

        logger.info("Writing c3proj file")
        with open(os.path.join(self.tempPath, 'project.c3proj'), 'w') as outfile:
            json.dump(self.pFiles['c3proj'], outfile, indent=4)

        #creating c3 files
        
        for fileKey, fileValue in self.pFiles['files'].items():
            
            if len(fileValue['fList']) > 0:
                logger.info("Writing <" + fileKey + ">files...")
                folderName = os.path.join(self.tempPath, fileValue['folderName'])
                if not os.path.exists(folderName):
                    os.makedirs(folderName)
                
                for currentFile in fileValue['fList']:
                    logger.info("File name: " + currentFile.name)
                    if fileKey in self.c3FileList:
                        with open(os.path.join(folderName, currentFile.name), 'w') as outfile:
                            json.dump(currentFile.content, outfile, indent=4)
                    else:
                        with open(os.path.join(folderName, currentFile.name), "wb") as binary_file:
                            binaryFormat = bytearray(currentFile.content)
                            binary_file.write(binaryFormat)

        #exporting project
        if  not os.path.exists(export_path):
            os.makedirs(export_path)

        if one_file:
            logger.info("Compressing project into .c3p file...")
            zipPath = os.path.join(export_path, name + ".c3p")
            dirPath = self.tempPath
        
            zipf = zipfile.ZipFile(zipPath , mode='w')
            lenDirPath = len(dirPath)
            for root, _ , files in os.walk(dirPath):
                for file in files:
                    filePath = os.path.join(root, file)
                    zipf.write(filePath , filePath[lenDirPath :] )
            zipf.close()

        else:
            logger.info("Exporting project to target parth...")
            self.copyFiles(self.tempPath, export_path)

        if one_file:
            logger.info("File created '" + name + ".c3p' at '" + export_path + "'")
        else:
            logger.info("Project exported at path: " + export_path)    
        shutil.rmtree(self.tempPath)
        

    def copyFiles(self, src, dst):
        logger.info('src: ' + src)
        fileList = []
        for f in os.listdir(src):
            fileList.append(f)

        for filename in fileList:
            filename= os.path.join(src, filename)
            if os.path.isfile(filename):
                shutil.copy(filename, dst)
            else:
                destFolder = os.path.join(dst, os.path.basename(filename)) 
                if not os.path.exists(destFolder):
                    os.mkdir(destFolder)
                    self.copyFiles( filename, destFolder )
    
    #updates c3proj file and sids according to the loaded files
    def updateC3proj(self):

        logger.info("Updating .c3proj file")
        for fKey, fValue in self.pFiles['files'].items():
            if fValue['supported'] and fValue['metaData']:
             
                updatedDir = {'items' : [], 'subfolders' : []}
                

                for c3File in self.pFiles['files'][fKey]['fList']:                    

                    tempDir = updatedDir

                    #for each file's directory
                    for fDir in c3File.dir:
                        
                        createDir = True
                        
                        tempDir = tempDir['subfolders']
                        for j, c3Dir in enumerate(tempDir):
                            
                            if fDir == c3Dir['name']:
                                tempDir = tempDir[j]
                                createDir = False
                                break
                        
                        if createDir:
                            logger.info("new dir: " + fDir)
                            tempDir.append({'items' : [], 'subfolders' : [], 'name' : fDir})
                            tempDir = tempDir[len(tempDir)-1]
                    
                    if fValue['c3File'] == True:
                        tempDir['items'].append(c3File.content['name'])
                    else:
                        tempDir['items'].append({'name' : c3File.name, 'type' : c3File.type, 'sid' : 0})
                        
                    
                if fValue['c3File']:
                    self.pFiles['c3proj'][fKey] = updatedDir
                else:
                    self.pFiles['c3proj']['rootFileFolders'][fKey] = updatedDir

        # Set new values to project sids and uids. Very unlikely for this to be necessary, it's probabilly safier to leave this commented
        # self.setProjectIds()
        



    def addC3File(self, c3File):
        pass

    def setProjectIds(self):
        
        logger.info("Seting sids for c3proj...")
        self.pFiles['c3proj'] = self.setFileSid(self.pFiles['c3proj'])
        
        
        for key, value in self.pFiles['files'].items():
            
            if value['supported'] and value['c3File']:
                logger.info("Seting sids for files <" + key + ">")
                for f in value['fList']:
                    
                    logger.info("file: " + f.name)
                    f.content = self.setFileSid(f.content)

        logger.info ("All sids seted")

    def setFileSid(self, jsonFile):

        jsonStr = json.dumps(jsonFile)

        pattern = re.compile(r'("sid": *)(\d+)')        
        result = re.subn(pattern, self.newSid, jsonStr)

        pattern = re.compile(r'("uid": *)(\d+)')        
        result = re.subn(pattern, self.newUid, result[0]) 

        jsonFile = json.loads(result[0])
        return jsonFile
                

    def newSid(self, string):
        self.sid += 1
        return '"sid": ' + str(self.sid)
    
    def newUid(self, string):
        self.uid += 1
        return '"uid": ' + str(self.uid)

    def getGlobalVarList(self):

        globalVarList = []

        for f in self.pFiles['files']['eventSheets']['fList']:
            for event in f.content['events']:
                if event['eventType'] == 'variable':
                    globalVarList.append(event['name'])

        return globalVarList

    def getGroupList(self):

        groupList = []

        for f in self.pFiles['files']['eventSheets']['fList']:
            groupList += self.getGroupInEvents(f.content['events'])
        
        return groupList

    def getGroupInEvents(self, events):

        groupList = []

        for event in events:
            if event['eventType'] == 'group':
                groupList.append(event['title'])

            if 'children' in event:
                groupList += self.getGroupInEvents(event['children'])

        return groupList


def main():
    
    '''
    targetProjectA = C3Project('test/files/projects/oneFileProject.c3p')
    targetProjectA.exportProject(export_path='export/projectA', one_file=False)
    
    targetProjectB = C3Project('test/files/projects/testProject.c3p')

    targetProjectB.removeC3File('objectTypes', 'keyboard.json')
    targetProjectB.removeC3File('sound', 'sfx_sample.webm')    

    
    targetProjectB.exportProject(export_path='export/projectB', one_file=False)
    '''
    
    targetProjectC = C3Project('test/spookids2.c3p')
    targetProjectC.exportProject(export_path='export/projectC', one_file=False)
    
    '''
    targetProjectD = C3Project('test/files/projects/isoengine.c3p')
    targetProjectD.exportProject(export_path='export/projectD', one_file=False)
    '''

if __name__== "__main__":
    main()