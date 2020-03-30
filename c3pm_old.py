import json
import re
import shutil
import os
from os import walk
from os.path import basename
import zipfile


import include.formatFilename

folders = {"project": {"root" : "temp\\project"}, "pack": {'root' : "temp\\pack", "families" : "temp\\pack\\families", "eventSheets" : "temp\\pack\\eventSheets", "images" : "temp\\pack\\images", "objectTypes" : "temp\\pack\\objectTypes", "info" : "temp\\pack"}}

def zipDir(dirPath, zipPath):
    zipf = zipfile.ZipFile(zipPath , mode='w')
    lenDirPath = len(dirPath)
    for root, _ , files in os.walk(dirPath):
        for file in files:
            filePath = os.path.join(root, file)
            zipf.write(filePath , filePath[lenDirPath :] )
    zipf.close()            

def exportPack_checkObjectInExpression(expression):
    
    expressionObjectList = []

    #remove strings
    expression = re.sub('\\\"(.*?)\\\"', '', expression)

    #match objects
    match = re.findall(r'(\w+)\.[^ ]*', expression)
    if match:
        for obj in match:
            if obj not in expressionObjectList:
                expressionObjectList.append(obj)


    return expressionObjectList

def exportPack_findObjects(events):
    
    fullObjectList = []
    
    for event in events:
        if (event["eventType"] ==  "block"):
            for eventKey, eventValue in event.items():
                
                if(eventKey == "conditions" or eventKey == "actions"):
                    for ace in eventValue:
                        if ("parameters" in ace):
                            for parameterKey, parameterValue in ace["parameters"].items():
                                expressionObjList = exportPack_checkObjectInExpression(parameterValue)
                                for obj in expressionObjList:
                                    if obj not in fullObjectList:
                                        fullObjectList.append(obj)
                        
                        
                        if ace["objectClass"] not in fullObjectList:
                            fullObjectList.append(ace["objectClass"])
                elif(eventKey == "children"):
                    tempList = exportPack_findObjects(event["children"])
                    for obj in tempList:
                        if obj not in fullObjectList:
                            fullObjectList.append(obj)
                    
    
    return fullObjectList

def exportPack_getEventSheetObjects(projectPath, eventSheetName, eventSheetList):
    
    objectList = []
    tempList = []

    #load event sheet
    eventSheet = ""
    with open(projectPath + "\eventSheets\\" + eventSheetName + ".json") as json_file:
        eventSheet = json.load(json_file)

    if eventSheet not in eventSheetList:
        eventSheetList.append(eventSheetName)    

    tempList += exportPack_findObjects(eventSheet['events'])

    for event in eventSheet["events"]:
        if event['eventType'] == "include":
            if event['includeSheet'] not in eventSheetList:
                temp = exportPack_getEventSheetObjects(projectPath, event["includeSheet"], eventSheetList)
                tempList += temp
            
    for item in tempList:
        if item not in objectList:
            objectList.append(item)


    return objectList

def exportPack_getPackData(projectPath, fullObjectList):
    
    imageFileList = []
    objectTypeFileList = []
    familyFileList = []
 
    #copy object files, families and images
    for (dirpath, dirnames, filenames) in walk(projectPath + "\objectTypes"):
        objectTypeFileList.extend(filenames)
        break

    for (dirpath, dirnames, filenames) in walk(projectPath + "\\families"):
        familyFileList.extend(filenames)
        break
    

    familyObjList = []
    objectTypeList = []

    for obj in fullObjectList:
        tempFileName = obj.lower() + ".json"
        
        for familyFile in familyFileList:
            if tempFileName == familyFile:
                familyJson = {}
        
                with open(projectPath + "\\families\\" + familyFile) as json_file:
                    familyJson = json.load(json_file)
        
                familyObjList.append(obj)
        
                for familyMenber in familyJson['members']:
                    if familyMenber not in objectTypeList:
                        objectTypeList.append(familyMenber)
   
        for objectTypeFile in objectTypeFileList:
            if tempFileName == objectTypeFile:
                if obj not in objectTypeList:
                    objectTypeList.append(obj)

    return {'objectTypes' : objectTypeList, 'families' : familyObjList}
    
def exportPack_infoFile(projectPath, packName, author, version, eventSheetName):

    #set info.json
    infoJson = {"packName" : "pack name", "author" : "author name", "version" : "1.0.0.0", "data" : {}}
    eventSheetList = []

    infoJson["packName"] = packName
    infoJson["author"] = author
    infoJson["version"] = version

    allObjectList = exportPack_getEventSheetObjects(projectPath, eventSheetName, eventSheetList)
    infoJson["data"]["eventSheets"] = eventSheetList

    tempData = exportPack_getPackData(projectPath, allObjectList)
    infoJson["data"]["objectTypes"] = tempData["objectTypes"]
    infoJson["data"]["families"] = tempData["families"]

    return infoJson

def exportPack_copyFiles(projectPath, info):
    


    # copy event sheets, objectTypes and families

    fileTypes = ['objectTypes', 'families', 'eventSheets']

    for fileType in fileTypes:
        for fileName in os.listdir(projectPath + "\\" + fileType):
            
            for item in info['data'][fileType]:
                formatedFileName = item.lower() + '.json'

                if formatedFileName == fileName:
                    source = projectPath + '\\' + fileType + '\\' + fileName
                    destination = folders['pack'][fileType] + '\\' + fileName
                    shutil.copyfile(source, destination)

    # copy images

    for fileName in os.listdir(projectPath + "\\images"):
        for item in info['data']['objectTypes']:

            if fileName.find(item.lower()) >= 0:
                    source = projectPath + '\\images\\' + fileName
                    destination = folders['pack']['images'] + '\\' + fileName
                    shutil.copyfile(source, destination)

def exportPack(projectPath, packPath, packName, author, version, eventSheetName):

    print("Exporting pack...")
        
    try:
        
        #create temp file folders
        for folderType in ['project', 'pack']:
            for folderKey, forlderPath in folders[folderType].items():
                if not os.path.exists(forlderPath):
                    os.makedirs(forlderPath)

        #unzip c3p files
        with zipfile.ZipFile(projectPath, 'r') as zip_ref:
            zip_ref.extractall(folders['project']['root'])

        extractedProjectPath = folders['project']['root']

        #create info.json file
        info = exportPack_infoFile(extractedProjectPath, packName, author, version, eventSheetName)
        
        with open(folders['pack']['info'] + '\info.json', 'w') as f:
            json.dump(info, f)

        #copy files
        exportPack_copyFiles(extractedProjectPath, info)

        #create c3pack file
        filename = include.formatFilename.format_filename(packName)
        zipDir(folders['pack']['root'], packPath + "\\" + filename + '.c3pack')
        

        #remove temp files
        if os.path.exists('temp'):
            shutil.rmtree("temp")
    
        print("Pack exported!")

    except Exception as e:

        print("Oops... We had an issue: ")
        print(e)
    
def importPack_extractFiles():

    for fileType in ['images', 'objectTypes', 'families', 'eventSheets']:
        
        if not os.path.exists(folders['project']['root'] + "\\" + fileType):
            os.makedirs(folders['project']['root'] + "\\" + fileType)

        for fileName in os.listdir(folders['pack']['root'] + "\\" + fileType):
            
            source = folders['pack']['root'] + '\\' + fileType + '\\' + fileName
            destination = folders['project']['root'] + '\\' + fileType + '\\' + fileName
            if (not os.path.exists(destination)):
                shutil.copyfile(source, destination)
            else:
                raise ValueError("Error! This file already exists in the project: " + fileName)

def importPack(projectPath, packPath):
    
    #create temp file folders
    for folderType in ['project', 'pack']:
        for folderKey, forlderPath in folders[folderType].items():
            if not os.path.exists(forlderPath):
                os.makedirs(forlderPath)

    #unzip c3p files
    with zipfile.ZipFile(projectPath, 'r') as zip_ref:
        zip_ref.extractall(folders['project']['root'])

    #unzip c3p files
    with zipfile.ZipFile(packPath, 'r') as zip_ref:
        zip_ref.extractall(folders['pack']['root'])

    importPack_extractFiles()

    # #remove temp files
    # if os.path.exists('temp'):
    #     shutil.rmtree("temp")

def main():
        
    
    exportPack("C:\\Users\\renan\\Desktop\\c3pmTest\\export_project.c3p", "C:\\Users\\renan\\Desktop\\c3pmTest","Pack name", "Author name", "1.0.0.0", "packTest")
    importPack("C:\\Users\\renan\\Desktop\\c3pmTest\\import_project.c3p", "C:\\Users\\renan\\Desktop\\c3pmTest\\Pack_name.c3pack")

if __name__== "__main__":
    main()