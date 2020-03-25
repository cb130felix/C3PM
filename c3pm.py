import json
import re

def checkObjectinExpression(expression):
    
    expressionObjectList = []

    expression = re.sub('\\\"(.*?)\\\"', '', expression)

    match = re.findall(r'\b([\w]+\.)', expression)
    if match:
        for string in match:
            expressionObj = string.split(".")[0]
            if expressionObj not in expressionObjectList:
                expressionObjectList.append(expressionObj)
    else:
       pass

    return expressionObjectList

def findObjects(events, objectClassList):
    
    
    
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
                    findObjects(event["children"], objectClassList)
    
    return objectClassList


def main():

    proj = ""
    eventSheet = ""

    objectClassList = []


    with open("project\project.c3proj") as json_file:
        data = json.load(json_file)

    with open("project\eventSheets\event sheet 1.json") as json_file:
        eventSheet = json.load(json_file)


    findObjects(eventSheet["events"], objectClassList)
    
    print("Object lis: ", objectClassList)

main()