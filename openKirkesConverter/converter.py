#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela
import bs4
from bs4 import *
import re
import datetime

renewCountDelimiter = " / "
renewCountRegex = "([0-9]+" + renewCountDelimiter + "[0-9]+)"
dueDateRegex = "((?:[1-9]{1}.)|(?:[1-9]{2}.)){2}[0-9]+"
orderNoRegex = "([0-9]+)"
maxRenewDefault = 5

waiting = 0
in_transit = 1
available = 3

statuses = {'waiting': waiting, 'in_transit': in_transit, 'available': available}


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
                metadataElem = element.find('div', {'class': 'record-core-metadata'})
                type = None
                typeElem = element.find('span', {'class': 'label-info'})
                title = None
                author = None
                if titleElem is not None:
                    title = titleElem.text
                if typeElem is not None:
                    type = typeElem.text
                image = None
                image_elem = element.find('img', {'class': 'recordcover'})
                if metadataElem is not None:
                    authorUrl = metadataElem.find('a')
                    if authorUrl is not None:
                        author = authorUrl.text
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
                loans.append({'id': recordId, 'renewId': renewId, 'resource': {'id': recordId, 'title': title,'author': author, 'type': type, 'image': image}, 'renewsTotal': renewsTotal, 'renewsUsed': renewsUsed,
                              'dueDate': dueDate})
            return loans
    return None


# Get the loans from HTML
def extractHolds(baseURL, html):
    pageContent = BeautifulSoup(html, 'html.parser')
    table = pageContent.find('table', {'class': 'myresearch-table'})
    if table is not None:
            holdsHtml = table.findAll('tr', {'class': 'myresearch-row'})
            holds = []
            for element in holdsHtml:
                recordId = None
                inputOne = element.find('input', {'type': 'hidden', 'name': 'cancelSelectedIDS[]'})
                inputTwo = element.find('input', {'type': 'hidden', 'name': 'cancelAllIDS[]'})
                titleElem = element.find('a', {'class': 'record-title'})
                plElem = element.find('span', {'class': 'pickupLocationSelected'})
                plRoot = element.find('div', {'class': 'pickup-location-container'})
                metadataElem = element.find('div', {'class': 'record-core-metadata'})
                status = waiting
                transit_elem = element.find('div', {'class': 'text-success'})
                avail_elem = element.find('div', {'class': 'alert alert-success'})

                type = None
                typeElem = element.find('span', {'class': 'label-info'})
                title = None
                author = None
                order_num = None
                if metadataElem is not None:
                    authorUrl = metadataElem.find('a')
                    if authorUrl is not None:
                        author = authorUrl.text
                currentPickupLocation = None
                if plElem is not None:
                    currentPickupLocation = plElem.text
                elif plRoot is not None:
                    lparts = plRoot.text.split(":")
                    if len(lparts) > 1:
                        currentPickupLocation = lparts[1].replace("  ", "").replace("\n", "")
                if titleElem is not None:
                    title = titleElem.text
                    recordId = titleElem.attrs.get("href").replace("/Record/", "")
                if typeElem is not None:
                    type = typeElem.text
                image = None
                image_elem = element.find('img', {'class': 'recordcover'})
                if image_elem is not None:
                    image = baseURL+image_elem.attrs.get("src")
                actionId = None
                cancelPossible = False
                if inputOne is not None:
                    cancelPossible = not inputOne.has_attr("disabled")
                    if inputTwo.has_attr("value"):
                        actionId = inputOne.attrs.get('value')
                elif inputTwo is not None:
                    cancelPossible = not inputTwo.has_attr("disabled")
                    if inputTwo.has_attr("value"):
                        actionId = inputTwo.attrs.get('value')

                if transit_elem is not None and not cancelPossible:
                    status = in_transit
                elif avail_elem is not None and not cancelPossible:
                    status = available
                    availText = avail_elem.text
                    orderNoSearch = re.findall(orderNoRegex, availText)
                    numString = ""

                    if orderNoSearch is not None:
                        for numObj in orderNoSearch:
                            numString += numObj
                        if len(numString) > 0:
                            order_num = int(numString)

                book_pickup = {'pickup_location': currentPickupLocation, 'order_number': order_num}

                holds.append({'id': recordId, 'actionId': actionId, 'status': status, 'cancel_possible': cancelPossible, 'pickup': book_pickup, 'resource': {'id': recordId, 'title': title,'author': author, 'type': type, 'image': image}})
            return holds
    return None
