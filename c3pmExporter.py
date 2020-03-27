import json
import re
import shutil
import os
from os import walk
import zipfile


import include.formatFilename



folders = {"output": "output", "families" : "output\\temp\\families", "eventSheets" : "output\\temp\\eventSheets", "images" : "output\\temp\\images", "objectTypes" : "output\\temp\\objectTypes", "info" : "output\\temp\\"}

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

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
                    destination = folders[fileType] + '\\' + fileName
                    shutil.copyfile(source, destination)

    # copy images

    for fileName in os.listdir(projectPath + "\\images"):
        for item in info['data']['objectTypes']:

            if fileName.find(item.lower()) >= 0:
                    source = projectPath + '\\images\\' + fileName
                    destination = folders['images'] + '\\' + fileName
                    shutil.copyfile(source, destination)

def exportPack(projectPath, packPath, packName, author, version, eventSheetName):

    #remove old temp files
    if os.path.exists('temp'):
        shutil.rmtree("temp")

    #create temp file folders
    for folderKey, forlderPath in folders.items():
        if not os.path.exists(forlderPath):
            os.makedirs(forlderPath)

    #create info.json file
    info = exportPack_infoFile(projectPath, packName, author, version, eventSheetName)
    
    with open(folders['info'] + '\info.json', 'w') as f:
        json.dump(info, f)

    #copy files
    exportPack_copyFiles(projectPath, info)

    #create c3pack file
    filename = include.formatFilename.format_filename(packName)
    zipf = zipfile.ZipFile( packPath + "\\" + filename + '.c3pack', 'w', zipfile.ZIP_DEFLATED)
    zipdir('temp/', zipf)
    zipf.close()

    #print(info)
    
def main():
    try:
        exportPack("F:\\Github\\C3PM\\project", "F:\\Github\\C3PM\\output","Pack name", "Author name", "1.0.0.0", "Event sheet 1")
        print("Pack exported!")
    except Exception as e:
        print(e)

if __name__== "__main__":
    main()