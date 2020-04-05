import json
import shutil
import os
from os import walk
from os.path import basename
import zipfile


folders = {'sourceProject' : {'source' : '', 'root' : 'temp\\sourceProject'}, 'targetProject' : {'source' : '', 'root' : 'temp\\targetProject'}}

def zipDir(dirPath, zipPath):
    zipf = zipfile.ZipFile(zipPath , mode='w')
    lenDirPath = len(dirPath)
    for root, _ , files in os.walk(dirPath):
        for file in files:
            filePath = os.path.join(root, file)
            zipf.write(filePath , filePath[lenDirPath :] )
    zipf.close()    

fileTypeList = {
    'eventSheets' : {'folderName' : 'eventSheets', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'true' },
    'families' : {'folderName' : 'families', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'true'},
    'objectTypes' : {'folderName' : 'objectTypes', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'true'},
    'layouts' : {'folderName' : 'layouts', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'true'},
    'timelines' : {'folderName' : 'timelines', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'true'},
    'ease' : {'folderName' : 'timelines//transitions', 'copyFiles' : 'true', 'metaData' : 'false', 'c3File' : 'true'},
    'images' : {'folderName' : 'images', 'copyFiles' : 'true', 'metaData' : 'false', 'c3File' : 'false'},
    'script' : {'folderName' : 'scripts', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'},
    'sound' : {'folderName' : 'sounds', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'},
    'music' : {'folderName' : 'music', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'},
    'video' : {'folderName' : 'videos', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'},
    'font' : {'folderName' : 'fonts', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'},
    'general' : {'folderName' : 'files', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'}
}


def importPack_extractFiles():
   
    
    #copy project files
    for fileTypeKey, fileTypeValue in fileTypeList.items():
        
        source = folders['sourceProject']['root'] + "\\" + fileTypeValue['folderName']
        dest = folders['targetProject']['root'] + "\\"  + fileTypeValue['folderName']

        if(os.path.exists(source)):
            fileTypeValue['copyFiles'] = 'true'
            if(not os.path.exists(dest)):
                os.mkdir(dest)

            src_files = os.listdir(source)
            for file_name in src_files:
                full_file_name = os.path.join(source, file_name)
                
                if os.path.isfile(full_file_name):
                    if(not os.path.exists(folders['targetProject']['root'] + "\\" + fileTypeValue['folderName'] + "\\" + file_name)):
                        shutil.copy(full_file_name, dest)
                    else:
                        raise ValueError("File already exists in the targeted project: " + file_name)
        else:
            fileTypeValue['copyFiles'] = 'false'
def importPack_updateMetaData():
    c3Proj = {'sourceProject' : {}, 'targetProject' : {}}

    #load project.c3proj
    for project in ['sourceProject', 'targetProject']:
        c3Proj[project] = ""
        with open(folders[project]['root'] + "\\project.c3proj") as json_file:
            c3Proj[project] = json.load(json_file)

        



    # update used addons
    c3Proj['targetProject']['usedAddons'] += c3Proj['sourceProject']['usedAddons']

    # update containers data
    c3Proj['targetProject']['containers'] += c3Proj['sourceProject']['containers']

    packageName = c3Proj['sourceProject']['name']
    # update c3 meta data

    for fileTypeKey, fileTypeValue in fileTypeList.items():

            if fileTypeValue['metaData'] == 'true' and fileTypeValue['copyFiles'] == 'true':

                # get source project file data

                c3pmFolder = {'items':[], 'subfolders' : [], 'name' : 'c3Packs'}
                fileData = {'items':[], 'subfolders' : [], 'name' : packageName}
                keyRootPath = {}
                
                if fileTypeValue['c3File'] == 'true':
                    keyRootPath['source'] = c3Proj['sourceProject'][fileTypeKey]
                    keyRootPath['target'] = c3Proj['targetProject'][fileTypeKey]
                else:    
                    keyRootPath['source'] = c3Proj['sourceProject']['rootFileFolders'][fileTypeKey]
                    keyRootPath['target'] = c3Proj['targetProject']['rootFileFolders'][fileTypeKey]
                
                fileData['items'] = keyRootPath['source']['items']
                fileData['subfolders'] = keyRootPath['source']['subfolders']
               
                # set target project file data
                
                folderIndex = 0
                createC3packFolder = True
                
                for c3folder in keyRootPath['target']['subfolders']:
    
                    if 'name' in c3folder:
                        if c3folder['name'] == 'c3Packs':
                            createC3packFolder = False
                            break
        
                    folderIndex = folderIndex + 1    
                    
                if createC3packFolder:
                    keyRootPath['target']['subfolders'].append(c3pmFolder)
                    folderIndex = len(keyRootPath['target']['subfolders']) -1
                        
                keyRootPath['target']['subfolders'][folderIndex]['subfolders'].append(fileData)
                            
    with open(folders['targetProject']['root'] + '\\' + '\\project.c3proj', 'w') as outfile:
        json.dump(c3Proj['targetProject'], outfile, indent=4)

def importPack(sourceProjecPath, targetProjectPath, useOriginalFile):
    

    try:
        folders['sourceProject']['source'] = sourceProjecPath
        folders['targetProject']['source'] = targetProjectPath

        # create c3p backup

        backupPath = folders['targetProject']['source'].split('.')[0] + "_backup.c3p"
        shutil.copy(folders['targetProject']['source'], backupPath)
        
        #remove old temp files
        if (os.path.exists('temp')):
            shutil.rmtree('temp')
        
        #unzip projects on temp folders
        for project in ['sourceProject', 'targetProject']:
            if (not os.path.exists(folders[project]['root'])):
                os.makedirs(folders[project]['root'])
            
            with zipfile.ZipFile(folders[project]['source'], 'r') as zip_ref:
                    zip_ref.extractall(folders[project]['root'])
        
        
        #c3pm magic
        importPack_extractFiles()
        importPack_updateMetaData()


        # export packed project
        
        zipPath = ""
        if(useOriginalFile):
            zipPath = folders['targetProject']['source']
        else:
            zipPath = folders['targetProject']['source'].split('.')[0] + "_c3packed.c3p"
        
        
        zipDir(folders['targetProject']['root'], zipPath)
        return {'status':'sucess', 'projectName' : zipPath}

    except Exception as e:
        raise
        return {'status':'fail', 'error':e}


def main():

    importPack("C:\\Users\\renan\\Desktop\\c3pmTest\\[c3pack] Color Blink r_18902.c3p", "C:\\Users\\renan\\Desktop\\c3pmTest\\sampleTemplate.c3p", False)
    importPack("C:\\Users\\renan\\Desktop\\c3pmTest\\[C3pack] Shadow Trail r_18902.c3p", "C:\\Users\\renan\\Desktop\\c3pmTest\\sampleTemplate_c3packed.c3p", False)
    
if __name__== "__main__":
    main()