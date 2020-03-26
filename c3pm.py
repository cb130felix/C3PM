import json
import re
import shutil
import os
from os import walk
import zipfile


import include.formatFilename

infoObj = {"packName" : "pack name", "author" : "author name", "version" : "1.0.0.0", "data" : {"objectTypes": [], "families" : []}}
folders = {"output": "output", "families" : "output\\temp\\families", "eventSheets" : "output\\temp\\eventSheets", "images" : "output\\temp\\images", "objectTypes" : "output\\temp\\objectTypes", "info" : "output\\temp\\"}

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def checkObjectinExpression(expression):
    
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

def findObjects(events):
    
    objectClassList = []
    
    for event in events:
        if (event["eventType"] ==  "block"):
            for eventKey, eventValue in event.items():
                
                if(eventKey == "conditions" or eventKey == "actions"):
                    for ace in eventValue:
                        if ("parameters" in ace):
                            for parameterKey, parameterValue in ace["parameters"].items():
                                expressionObjList = checkObjectinExpression(parameterValue)
                                for obj in expressionObjList:
                                    if obj not in objectClassList:
                                        objectClassList.append(obj)
                        
                        
                        if ace["objectClass"] not in objectClassList:
                            objectClassList.append(ace["objectClass"])
                elif(eventKey == "children"):
                    tempList = findObjects(event["children"])
                    for obj in tempList:
                        if obj not in objectClassList:
                            objectClassList.append(obj)
                        
    
    return objectClassList

def createObjectsTypes(projectPath, objectList):
    
    images = []
    
    #copy object files, families and images
    for (dirpath, dirnames, filenames) in walk(projectPath + "\images"):
        images.extend(filenames)
        break
    
    for objType in ["objectTypes", "families"]:
        
        files = []

        path = projectPath + "\\" + objType

        for (dirpath, dirnames, filenames) in walk(path):
            files.extend(filenames)
            break
        
        print(files)
        for obj in objectList:
            objFileName = (obj+".json").lower()

            if objFileName in files:
                
                original = r'' + projectPath + "\\" + objType + "\\" + obj + ".json"
                target = r'' + folders[objType] + '\\' + obj + ".json"

                shutil.copyfile(original, target)

                infoObj["data"][objType].append(obj)
                
                if objType == "objectTypes":
                    
                    for image in images:
                        if image.find(obj.lower()) >= 0:
                            
                            original = r'' + projectPath + "\images\\" + image
                            target = r'' + folders['images'] + '\\' + image

                            shutil.copyfile(original, target)

    #create info.json file
    with open(folders['info'] + '\info.json', 'w') as f:
        json.dump(infoObj, f)

def createFolders():

    
    for folderKey, forlderPath in folders.items():
        if not os.path.exists(forlderPath):
            os.makedirs(forlderPath)
    

def exportPack(projectPath, packName, author, version, sheetName):
    
    infoObj["packName"] = packName
    infoObj["author"] = author
    infoObj["version"] = version
    
    if os.path.exists('temp'):
        shutil.rmtree("temp")

    createFolders()

    proj = ""
    eventSheet = ""

    objectClassList = []


    with open(projectPath + "\project.c3proj") as json_file:
        c3proj = json.load(json_file)

    with open(projectPath + "\eventSheets\\" + sheetName + ".json") as json_file:
        eventSheet = json.load(json_file)

    #copy eventSheet
    original = r'' + projectPath + "\eventSheets\\" + sheetName + '.json'
    target = r'' + folders['eventSheets'] + "\\" + sheetName + '.json'


    shutil.copyfile(original, target)

    objectClassList = findObjects(eventSheet["events"])
    createObjectsTypes(projectPath, objectClassList)
    
    filename = include.formatFilename.format_filename(packName)
    zipf = zipfile.ZipFile( folders['output'] + "\\" + filename + '.c3pack', 'w', zipfile.ZIP_DEFLATED)
    zipdir('temp/', zipf)
    zipf.close()



def main():
    createFolders()
    exportPack("F:\Github\C3PM\project", "Pack name", "Author name", "1.0.0.0", "event sheet 1")
    print(infoObj)

if __name__== "__main__":
    main()