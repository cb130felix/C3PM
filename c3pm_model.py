import C3Project as c3p
import re
import json
import copy
import logging

# setting lof configs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler =  logging.FileHandler('log.txt')
file_handler.setFormatter(formatter)

console = logging.StreamHandler()

logger.addHandler(file_handler)
logger.addHandler(console)

#---------------------------------------------------------

def getDuplicates(dataList):
    
    tempList = []
    duplicateList = []

    for item in dataList:
        if item in tempList: duplicateList.append(item)
        tempList.append(item)
        
    return duplicateList




class C3PM:

    mergeSteps = 4
    ignoreFileList = ['icon', 'timelines', 'ease']

    def __init__(self, projectPath, packPath, overwriteFiles=False, setDefaultFolders=True):
        self.overwriteFiles = overwriteFiles
        self.setDefaultFolders = setDefaultFolders
        self.secondaryProject = c3p.C3Project(packPath)
        self.mainProject = c3p.C3Project(projectPath)
        self.projectList = []

        self.mergeProjects()


    def mergeProjects(self):
        
        self.mergeProgress = 0
        self.currentStep = 0


        packName = self.secondaryProject.pFiles['c3proj']['name']
        packAuthor = "Anonymous"        

        if self.secondaryProject.pFiles['c3proj']['properties']['author'] != "":
            packAuthor = self.secondaryProject.pFiles['c3proj']['properties']['author']

        self.mergedProject = copy.deepcopy(self.mainProject)

        
        logger.info("Importing pack " + self.secondaryProject.pFiles['c3proj']['name'] + " into project " + self.mainProject.pFiles['c3proj']['name'] + "...")
        self.currentStep += 1        
        
        # merge project files
        logger.info("Checking duplicated files...")
        for fKey, fValue in self.secondaryProject.pFiles['files'].items():
            
            if fKey in self.ignoreFileList : continue

            for f in fValue['fList']:
                mFileList = self.mergedProject.pFiles['files'][fKey]['fList']
                addFile = True

                # check for duplicated single global instance objects
                for mFile in mFileList:
                    
                    if fKey in c3p.C3Project.c3FileList:
                        if 'singleglobal-inst' in f.content:
                            if f.content['plugin-id'] == mFile.content['plugin-id']:
                                if f.content['name'] == mFile.content['name']:
                                    addFile = False
                                    continue
                                else:
                                    raise NameError('Not possible to import a pack with duplicated single global instance <'+ f.content['plugin-id'] +'> with diferent name <' + f.content['name'] + '>')
                
                    if f.name == mFile.name:
                        if self.overwriteFiles:
                            self.mergedProject.pFiles['files'][fKey]['fList'].remove(mFile)
                        else:
                            raise NameError('Duplicated <' + fKey + '> file found: ' + f.name)

                if addFile:
                    
                    tempF = copy.deepcopy(f)
                    
                    if self.setDefaultFolders:
                        
                        tempF.dir.insert(0, packName + " by " + packAuthor)
                        tempF.dir.insert(0, 'C3PM')

                        print(tempF)
                    
                    self.mergedProject.pFiles['files'][fKey]['fList'].append(tempF)


        self.currentStep += 1

        logger.info("Updating plugins info...")
        self.mergedProject.pFiles['c3proj']['usedAddons'] += (self.secondaryProject.pFiles['c3proj']['usedAddons'])

        logger.info("Updating containers...")
        self.mergedProject.pFiles['c3proj']['containers'] += (self.secondaryProject.pFiles['c3proj']['containers'])

        projectGlobals = self.mergedProject.getGlobalVarList()
        duplicatedGlobals = getDuplicates(projectGlobals)
        
        if duplicatedGlobals:
            raise NameError('Duplicated global variable(s) found: ' + str(duplicatedGlobals))
        
        projectGroups = self.mergedProject.getGroupList()
        duplicatedGroups = getDuplicates(projectGroups)
        
        if duplicatedGroups:
            raise NameError('Duplicated global variable(s) found: ' + str(duplicatedGroups))
        

        
        
        '''
        logger.info("Checking for duplicated global vars...")
        projectGlobals = self.mainProject.getGlobalVarList()
        packGlobals = self.secondaryProject.getGlobalVarList()

        for packGlobal in packGlobals:
            if packGlobal in projectGlobals:
                raise NameError('Duplicated global variable: ' + packGlobal)
        self.currentStep += 1

        logger.info("Checking for duplicated groups...")
        projectGroups = self.mainProject.getGroupList()
        packGroups = self.secondaryProject.getGroupList()

        for packGroup in packGroups:
            if packGroup in projectGroups:
                raise NameError('Duplicated group: ' + packGroup)
        self.currentStep += 1
        '''
        
        logger.info("Project merged succesfully!")
        return self.mergedProject
                    
        

if __name__== "__main__":
    
    import c3pm_test