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

class C3PM:

    mergeSteps = 4
    
    ignoreFileList = ['icon', 'timelines', 'ease']

    def __init__(self, projectPath, packPath, overwriteFiles=False):
        self.overwriteFiles = overwriteFiles
        self.c3pack = c3p.C3Project(packPath)
        self.mainProject = c3p.C3Project(projectPath)
        self.projectList = []

        self.mergeProjects()

    def setMainProject(self, c3Project):
        self.mainProject = c3Project

    def addProjectToMerge(self, c3Project):
        self.projectList.append(c3Project)

    def mergeProjects(self):
        
        self.mergeProgress = 0
        self.currentStep = 0


        packName = self.c3pack.pFiles['c3proj']['name']
        packAuthor = "Anonymous"        

        if self.c3pack.pFiles['c3proj']['properties']['author'] != "":
            packAuthor = self.c3pack.pFiles['c3proj']['properties']['author']

        self.packedProject = copy.deepcopy(self.mainProject)

        
        logger.info("Importing pack " + self.c3pack.pFiles['c3proj']['name'] + " into project " + self.mainProject.pFiles['c3proj']['name'] + "...")
        self.currentStep += 1        
        
        # merge project files
        logger.info("Checking duplicated files...")
        for fKey, fValue in self.c3pack.pFiles['files'].items():
            
            if fKey in self.ignoreFileList : continue

            for f in fValue['fList']:
                packedFileList = self.packedProject.pFiles['files'][fKey]['fList']
                addFile = True

                # check for duplicated single global instance objects
                for packedFile in packedFileList:
                    
                    if fKey in c3p.C3Project.c3FileList:
                        if 'singleglobal-inst' in f.content:
                            if f.content['plugin-id'] == packedFile.content['plugin-id']:
                                if f.content['name'] == packedFile.content['name']:
                                    addFile = False
                                    continue
                                else:
                                    raise NameError('Not possible to import a pack with duplicated single global instance <'+ f.content['plugin-id'] +'> with diferent name <' + f.content['name'] + '>')
                
                    if f.name == packedFile.name:
                        if self.overwriteFiles:
                            packedFileList.remove(packedFile)
                        else:
                            raise NameError('Duplicated <' + fKey + '> file found: ' + f.name)

                if addFile:

                    f.dir.insert(0, packName + " by " + packAuthor)
                    f.dir.insert(0, 'C3PM')
                    packedFileList.append(f)
        self.currentStep += 1

        logger.info("Updating plugins info...")
        self.packedProject.pFiles['c3proj']['usedAddons'] += (self.c3pack.pFiles['c3proj']['usedAddons'])

        logger.info("Updating containers...")
        self.packedProject.pFiles['c3proj']['containers'] += (self.c3pack.pFiles['c3proj']['containers'])


        logger.info("Checking for duplicated global vars...")
        projectGlobals = self.mainProject.getGlobalVarList()
        packGlobals = self.c3pack.getGlobalVarList()

        for packGlobal in packGlobals:
            if packGlobal in projectGlobals:
                raise NameError('Duplicated global variable: ' + packGlobal)
        self.currentStep += 1

        logger.info("Checking for duplicated groups...")
        projectGroups = self.mainProject.getGroupList()
        packGroups = self.c3pack.getGroupList()

        for packGroup in packGroups:
            if packGroup in projectGroups:
                raise NameError('Duplicated group: ' + packGroup)
        self.currentStep += 1

        
        logger.info("Project merged succesfully!")
        return self.packedProject
                    
        

if __name__== "__main__":
    import c3pm_test