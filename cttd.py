# -*- coding: utf-8 -*-
"""
@Title: Cycle Time To Date (CTTD)
@Description: Calculates the cycle time of all Active work items

@usage: python3 -W ignore cttd.py

@author: Ian Carroll
"""

import requests
import json
import base64
import pprint
from datetime import datetime

# get access token here: https://dev.azure.com/instance/project/_usersSettings/tokens
personal_access_token = ""
username = ""

baseUrl = "https://dev.azure.com/instance/project/_apis/"

queryFilter = {'query': "select [System.Id],\
    [System.AreaPath],\
    [System.WorkItemType],\
    [System.Title],\
    [System.BoardColumn],\
    [System.State],\
    [System.Tags],\
    [Microsoft.VSTS.Scheduling.Size]\
     from WorkItems where ([System.AreaPath]='areapath') and \
     ([System.WorkItemType]='User Story' or \
        [System.WorkItemType]='Bug') and \
    [System.State]='Active'"}


def getWorkItemHistory(id):
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' +\
        base64.b64encode(personal_access_token.encode('utf-8'))

    url = (baseUrl + "wit/workitems/" + str(id) + "/revisions?api-version=5.1")
    itemresponse = requests.get(
        url,
        headers=headers,
        auth=(username, personal_access_token),
        verify=False)
    return(json.loads(itemresponse.text))


def getWorkItem(id):
    headers = {}
    headers['Content-type'] = "application/json"
    headers['Authorization'] = b'Basic ' +\
        base64.b64encode(personal_access_token.encode('utf-8'))

    url = (baseUrl + "wit/workitems/" + str(id) + "?api-version=5.1")
    itemresponse = requests.get(
        url,
        headers=headers,
        auth=(username, personal_access_token),
        verify=False)
    return(json.loads(itemresponse.text))


def byAge(e):
    return e['age']


def cleanDate(d):
    if "." in d:
        dt = datetime.strptime(str(d), '%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        dt = datetime.strptime(str(d), '%Y-%m-%dT%H:%M:%SZ')
    return dt


headers = {}
headers['Content-type'] = "application/json"
headers['Authorization'] = b'Basic ' +\
    base64.b64encode(personal_access_token.encode('utf-8'))

api_version = "5.1"

url = (baseUrl + "wit/wiql?api-version=%s" % (api_version))

response = requests.post(
    url,
    headers=headers,
    data=json.dumps(queryFilter),
    auth=(username, personal_access_token),
    verify=False)

workitems = json.loads(response.text)
print(len(workitems["workItems"]))
print("id,\
type,\
title,\
priority,\
state,\
createdDate,\
startDate,\
size,\
areapath,\
assignee")

currentid = 0

table = []

for work_item in workitems["workItems"]:
    newid = work_item["id"]

    details = getWorkItem(newid)
    itemfields = details["fields"]

    if "System.AssignedTo" in details["fields"]:
        assignee = details["fields"]["System.AssignedTo"]
    else:
        assignee = ""

    if "Microsoft.VSTS.Scheduling.Size" in itemfields:
        size = itemfields["Microsoft.VSTS.Scheduling.Size"]
    else:
        size = ""

    if "System.AreaPath" in itemfields:
        areapath = itemfields["System.AreaPath"]
    else:
        areapath = ""

    if "System.CreatedDate" in itemfields:
        createddate = itemfields["System.CreatedDate"]
    else:
        createddate = ""

    if "System.BoardColumn" in itemfields:
        boardColumn = itemfields["System.BoardColumn"]
    else:
        boardColumn = ""

    if "Microsoft.VSTS.Common.Priority" in itemfields:
        priority = itemfields["Microsoft.VSTS.Common.Priority"]
    else:
        priority = ""

    history = getWorkItemHistory(work_item["id"])

    oldest = 0
    found = False
    for value in history["value"]:
        fields = value["fields"]

        if "System.State" in fields:
            if fields["System.State"] == "Active":
                if found is False:
                    print(
                        str(newid) + "," +
                        fields["System.WorkItemType"] + ",\"" +
                        fields["System.Title"] + "\"," +
                        str(priority) + "," +
                        boardColumn + "," +
                        str(cleanDate(createddate)) + "," +
                        str(cleanDate(
                            fields["Microsoft.VSTS.Common.StateChangeDate"]
                            )) + "," +
                        str(size) + "," +
                        str(areapath) + ",\"" +
                        str(assignee["displayName"]) + "\"")
                    found = True
