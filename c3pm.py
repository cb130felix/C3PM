import json
import re

def checkObjectinExpression(expression):
    print(expression)
    m = re.search(r'\b([\w]+\.)', expression)
    print(m)




def findObjects(events):
    
    objectClassList = []
    
    for event in events:
        if (event["eventType"] ==  "block"):
            for eventKey, eventValue in event.items():
                
                if(eventKey == "conditions" or eventKey == "actions"):
                    for ace in eventValue:
                        if ("parameters" in ace):
                            for parameterKey, parameterValue in ace["parameters"].items():
                                checkObjectinExpression(parameterValue)
                        
                        
                        if ace["objectClass"] not in objectClassList:
                            objectClassList.append(ace["objectClass"])

    print("Object lis: ", objectClassList)


def main():
    proj = ""
    eventSheet = ""




    with open("project\project.c3proj") as json_file:
        data = json.load(json_file)

    with open("project\eventSheets\event sheet 1.json") as json_file:
        eventSheet = json.load(json_file)


    findObjects(eventSheet["events"])
    
    #print(eventSheet)

main()