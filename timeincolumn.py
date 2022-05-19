# -*- coding: utf-8 -*-
"""
@Title: Time in Column
@Description: Calculates the time in column of Active work items

@usage: python3 -W ignore timeincolumn.py

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

queryFilter = {'query': "select \
        [System.Id],\
        [System.AreaPath],\
        [System.WorkItemType],\
        [System.Title],\
        [System.BoardColumn],\
        [System.State] \
        from WorkItems \
        where \
        ([System.WorkItemType]='User Story' or [System.WorkItemType]='Bug') \
                and [System.State]='Active' and [System.AreaPath]='areapath'"}


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


def main():
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

    currentid = 0
    table = []

    for work_item in workitems["workItems"]:
        newid = work_item["id"]

        history = getWorkItemHistory(work_item["id"])
        item = getWorkItem(work_item["id"])
        itemfields = item["fields"]
        if "Microsoft.VSTS.Scheduling.Size" in itemfields:
            size = int(itemfields["Microsoft.VSTS.Scheduling.Size"])
        else:
            size = ""
        today = datetime.utcnow()
        assignee = ""
        oldest = 0
        found = False
        if "fields" in item:
            if "System.AssignedTo" in item["fields"]:
                assignee = item["fields"]["System.AssignedTo"]
            else:
                assignee = {"displayName": ""}

            if "System.BoardColumn" in item["fields"]:

                currentBoardColumn = item["fields"]["System.BoardColumn"]
                reason = item["fields"]["System.Reason"]
                oldcolumn = ""
                olddate = ""
                for value in history["value"]:

                    fields = value["fields"]
                    dt = ""
                    if "System.BoardColumn" in fields:

                        if "." in fields["System.ChangedDate"]:
                            dt = datetime.strptime(
                                fields["System.ChangedDate"],
                                '%Y-%m-%dT%H:%M:%S.%fZ')
                        else:
                            dt = datetime.strptime(
                                fields["System.ChangedDate"],
                                '%Y-%m-%dT%H:%M:%SZ')

                        found = True
                        daysaged = (today - dt).days
                        if oldcolumn != fields["System.BoardColumn"]:
                            oldcolumn = fields["System.BoardColumn"]

                            newdate = fields["System.ChangedDate"]
                            if newdate > olddate:
                                olddate = newdate

                        if daysaged < oldest:
                            oldest = daysaged
                if "." in newdate:
                    age = (today - datetime.strptime(
                            newdate,
                            '%Y-%m-%dT%H:%M:%S.%fZ')).days
                else:
                    age = (today - datetime.strptime(
                            newdate,
                            '%Y-%m-%dT%H:%M:%SZ')).days

                table.append({'column': fields["System.BoardColumn"],
                              'id': work_item["id"],
                              'type': fields["System.WorkItemType"],
                              'title': fields["System.Title"],
                              'age': age,
                              'size': size,
                              "assignedto": assignee["displayName"]})

    table.sort(reverse=True, key=byAge)

    print("id,type,title,column,days in column,size,assignee")
    for row in table:
        print(
            str(row["id"]) + "," +
            str(row["type"]) + ",\"" +
            str(row["title"]) + "\"," +
            str(row["column"]) + "," +
            str(row["age"]) + "," +
            str(row["size"]) + ",\"" +
            str(row["assignedto"]) + "\"")


if __name__ == "__main__":
    main()
