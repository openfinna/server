#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela
import bs4
from bs4 import *
import re
import datetime

renewCountDelimiter = " / "
renewCountRegex = "([0-9]+" + renewCountDelimiter + "[0-9]+)"
dueDateRegex = "((?:[1-9]{1}.)|(?:[1-9]{2}.)){2}[0-9]+"
maxRenewDefault = 5


# Get the CSRF Token from login dialog
def extractCSRF(html):
    loginDialog = BeautifulSoup(html, 'html.parser')
    csrfElement = loginDialog.find("input", {"name": "csrf"})
    if csrfElement is not None:
        if csrfElement.has_attr("value"):
            return csrfElement.attrs.get("value")
    return None


# Get the loans from HTML
def extractLoans(baseURL, html):
    pageContent = BeautifulSoup(html, 'html.parser')
    table = pageContent.find('table', {'class': 'myresearch-table'})
    if table is not None:
            loansHtml = table.findAll('tr', {'class': 'myresearch-row'})
            loans = []
            for element in loansHtml:
                recordId = element.attrs.get('id').replace('record', '')
                inputOne = element.find('input', {'type': 'hidden', 'name': 'renewAllIDS[]'})
                inputTwo = element.find('input', {'type': 'hidden', 'name': 'selectAllIDS[]'})
                titleElem = element.find('a', {'class': 'record-title'})
                type = None
                typeElem = element.find('span', {'class': 'label-info'})
                title = None
                if titleElem is not None:
                    title = titleElem.text
                if typeElem is not None:
                    type = typeElem.text
                image = None
                image_elem = element.find('img', {'class': 'recordcover'})
                if image_elem is not None:
                    image = baseURL+image_elem.attrs.get("src")
                textElements = element.findAll('strong')
                renewsTotal = maxRenewDefault
                renewsUsed = 0
                dueDate = None
                renewId = None
                if inputOne is not None:
                    if inputTwo.has_attr("value"):
                        renewId = inputOne.attrs.get('value')
                elif inputTwo is not None:
                    if inputTwo.has_attr("value"):
                        renewId = inputTwo.attrs.get('value')
                for text in textElements:
                    if re.search(renewCountRegex, text.get_text()) is not None:
                        renewCountNumbers = str(re.search(renewCountRegex, text.get_text()).group(1)).replace(
                            renewCountDelimiter, ",").split(",")
                        renewsUsed = int(renewCountNumbers[0])
                        renewsTotal = int(renewCountNumbers[1])
                    if re.search(dueDateRegex, text.get_text()) is not None:
                        date = re.search(dueDateRegex, text.get_text()).group(0)
                        dueDate = datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%Y/%m/%d")
                loans.append({'id': recordId, 'renewId': renewId, 'title': title, 'type': type, 'image': image, 'renewsTotal': renewsTotal, 'renewsUsed': renewsUsed,
                              'dueDate': dueDate})
            return loans
    return None
