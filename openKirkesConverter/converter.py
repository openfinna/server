#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela
import bs4
from bs4 import *
import re
import datetime

from openKirkesConnector.classes import *

renewCountDelimiter = " / "
renewCountRegex = "([0-9]+" + renewCountDelimiter + "[0-9]+)"
dueDateRegex = "((?:[1-9]{1}.)|(?:[1-9]{2}.)){2}[0-9]+"
expirationDateRegex = "(((?:[1-9]{1}.)|(?:[1-9]{2}.)){2}[0-9]+)"
orderNoRegex = "([0-9]+)"
hashKeyRegex = "^(.*)hashKey=([^#]+)"
price_regex = "^[^\d]*(\d+|\d+((,|\.)\d{1,2}))(\s|[a-zA-Z)]|€|$).*"
maxRenewDefault = 5

waiting = 0
in_transit = 1
available = 2

statuses = {'waiting': waiting, 'in_transit': in_transit, 'available': available}

municipal = 0
mobile = 1
library_types = {'municipal': municipal, 'mobile': mobile}


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
                image = baseURL + image_elem.attrs.get("src")
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
            loans.append({'id': recordId, 'renewId': renewId,
                          'resource': {'id': recordId, 'title': title, 'author': author, 'type': type, 'image': image},
                          'renewsTotal': renewsTotal, 'renewsUsed': renewsUsed,
                          'dueDate': dueDate})
        return loans
    return None


# Get the loans from HTML
def checkRenewResult(html, renew_id):
    pageContent = BeautifulSoup(html, 'html.parser')
    table = pageContent.find('table', {'class': 'myresearch-table'})
    if table is not None:
        loansHtml = table.findAll('tr', {'class': 'myresearch-row'})
        for element in loansHtml:
            inputOne = element.find('input', {'type': 'hidden', 'name': 'renewAllIDS[]'})
            inputTwo = element.find('input', {'type': 'hidden', 'name': 'selectAllIDS[]'})
            renewId = None
            if inputOne is not None:
                if inputTwo.has_attr("value"):
                    renewId = inputOne.attrs.get('value')
            elif inputTwo is not None:
                if inputTwo.has_attr("value"):
                    renewId = inputTwo.attrs.get('value')
            if renewId is not None:
                if renewId == renew_id:
                    result_elem = element.find('div', {'class': 'alert'})
                    if result_elem is not None:
                        classes = result_elem.attrs.get('class')
                        if "alert-success" in classes:
                            return RenewResult(result_elem.text)
                        else:
                            return ErrorResult(result_elem.text)
                    else:
                        header_msg = pageContent.find("div", {'class': 'flash-message alert'})
                        if header_msg is not None:
                            return ErrorResult(header_msg.text)
                        return ErrorResult("Renew failed")
    return ErrorResult("Something unexpected happened")


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

            status_box = element.find('div', {'class': 'holds-status-information'})
            queue = 0
            queue_elem = status_box.find('p')
            if queue_elem is not None:
                queue_parts = queue_elem.text.split(":")
                if len(queue_parts) > 0:
                    queue = int(queue_parts[1])

            expiration_date = None
            hold_date = None

            infobox_text = status_box.text
            date_elems = re.findall(expirationDateRegex, infobox_text)
            if date_elems is not None:
                hold_elem = date_elems.__getitem__(0)
                exp_elem = date_elems.__getitem__(1)
                if exp_elem is not None:
                    expiration_date = datetime.datetime.strptime(exp_elem[0], "%d.%m.%Y").strftime("%Y/%m/%d")
                if hold_elem is not None:
                    hold_date = datetime.datetime.strptime(hold_elem[0], "%d.%m.%Y").strftime("%Y/%m/%d")

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
                image = baseURL + image_elem.attrs.get("src")
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

            book_pickup = {'pickup_location': currentPickupLocation, 'reservation_number': order_num}
            holds.append({'id': recordId, 'actionId': actionId, 'status': status, 'cancel_possible': cancelPossible,
                          'pickup': book_pickup, 'queue': queue, 'expires': expiration_date, 'hold_date': hold_date,
                          'resource': {'id': recordId, 'title': title, 'author': author, 'type': type, 'image': image}})
        return holds
    return None


def extract_holing_details(html):
    pageContent = BeautifulSoup(html, 'html.parser')
    groupID_select = pageContent.find("select", {'id': 'requestGroupId'})
    info_text = ""
    info_text_elem = pageContent.find("p", {'class': 'helptext'})
    if info_text_elem is not None:
        info_text = info_text_elem.text
    types = []
    if groupID_select is not None:
        options = groupID_select.find_all("option")
        if options is not None and len(options) > 0:
            for option in options:
                option_name = option.text.strip()
                option_codename = None
                if option.has_attr("value"):
                    option_codename = option.attrs.get("value")
                types.append({
                    'id': option_codename,
                    'name': option_name
                })

    return {
        'types': types,
        'info': info_text
    }


def convertLibraryDetails(json_response):
    libDetails = []
    finna_list = json_response['list']
    for finna_lib in finna_list:
        id = finna_lib['id']
        name = finna_lib['name']
        short_name = finna_lib['shortName']
        slug = finna_lib['slug']
        type = municipal
        if finna_lib['type'] == "mobile":
            type = mobile
        email = finna_lib['email']
        homepage = finna_lib['homepage']
        location = {"street": finna_lib['address'].get('street', None),
                    "zipcode": finna_lib['address'].get('zipcode', None),
                    "city": finna_lib['address'].get('city', None), "matka_fi_url": finna_lib.get('routeUrl', None),
                    "maps_url": finna_lib.get('mapUrl'), "coordinates": finna_lib['address'].get('coordinates', None)}

        # Open Times parsing
        days = []
        finna_schedule = finna_lib['openTimes'].get('schedules', None)
        if finna_schedule is not None:
            for day in finna_schedule:
                date = datetime.datetime.strptime(day['date'] + datetime.datetime.now().strftime("%Y"),
                                                  "%d.%m.%Y").strftime("%Y/%m/%d")
                closed = day.get('closed', False)
                schedule = None
                if closed is False:
                    schedule = day['times'][0]
                day_obj = {
                    "date": date,
                    "closed": closed,
                    "schedule": schedule
                }
                days.append(day_obj)

        obj = {
            "id": id,
            "name": name,
            "short_name": short_name,
            "slug": slug,
            "type": type,
            "email": email,
            "homepage": homepage,
            "location": location,
            "days": days,
            "currently_open": finna_lib.get('openNow', False)
        }
        libDetails.append(obj)
    return libDetails


def convertResourceDetails(html):
    pageContent = BeautifulSoup(html, 'html.parser')
    items = pageContent.find_all("table", {'class': 'citation table table-striped'})
    result = {}
    if len(items) > 1:
        pos = 0
        for item in items:
            if pos == 1:
                detailsElem = item
                detail_rows = detailsElem.find_all('tr')
                for row in detail_rows:
                    name = row.find('th')
                    if name is not None:
                        name = name.text
                        value = row.find('td')
                        if value is not None:
                            value = value.text.replace("  ", "").strip()
                        result[name] = value
            pos = + 1
        return result
    return None


def extractHashKey(html):
    pageContent = BeautifulSoup(html, 'html.parser')
    hashkey_link = pageContent.find("a", {'class': 'placehold btn btn-primary hidden-print'})
    if hashkey_link is not None:
        if hashkey_link.has_attr("href"):
            hrefLink = hashkey_link.attrs.get("href")
            if re.search(hashKeyRegex, hrefLink) is not None:
                hashKey = re.search(hashKeyRegex, hrefLink).group(2)
                return hashKey
    return None


def getHomeLibraryResult(html):
    pageContent = BeautifulSoup(html, 'html.parser')
    successAlert = pageContent.find("div", {'class': 'flash-message alert alert-success'})
    return successAlert is not None


def getHomeLibrary(html):
    pageContent = BeautifulSoup(html, 'html.parser')
    home_lib_element = pageContent.find("select", {'id': 'home_library'})
    selected_element = home_lib_element.find("option", {'selected': 'selected'})
    selected = {
        "locationID": None,
        "locationDisplay": None
    }
    if selected_element is not None:
        if selected_element.has_attr("value"):
            selected['locationID'] = selected_element.attrs.get("value")
        selected['locationDisplay'] = selected_element.text
    return selected


def getUserDetails(html):
    pageContent = BeautifulSoup(html, 'html.parser')
    user = {
        "name": None,
        "library_preferences": {
            "full_name": None,
            "first_name": None,
            "surname": None,
            "address": None,
            "zipcode": None,
            "city": None,
            "phone_number": None,
            "email": None
        },
        "kirkes_preferences": {
            "email": None,
            "nickname": None
        }
    }
    fullname_elem = pageContent.find("span", {'class': 'username login-text'})
    if fullname_elem is not None:
        user['name'] = fullname_elem.text.strip()
        user['library_preferences']['full_name'] = fullname_elem.text.strip()

    lib_form = pageContent.find("form", {'id': 'profile_library_form'})
    kirkes_form = pageContent.find("form", {'name': 'my_profile_form'})
    if lib_form is not None:
        lib_values = lib_form.find_all("div", {'class': 'profile-text-value'})
        if len(lib_values) > 4:
            user['library_preferences']['first_name'] = lib_values[0].text
            user['library_preferences']['surname'] = lib_values[1].text
            user['library_preferences']['address'] = lib_values[2].text
            user['library_preferences']['zipcode'] = lib_values[3].text
            user['library_preferences']['city'] = lib_values[4].text
        lib_phone = lib_form.find("input", {'name': 'profile_tel'})
        if lib_phone is not None:
            if lib_phone.has_attr("value"):
                user['library_preferences']['phone_number'] = lib_phone.attrs.get("value")
        lib_email = lib_form.find("input", {'name': 'profile_email'})
        if lib_email is not None:
            if lib_email.has_attr("value"):
                user['library_preferences']['email'] = lib_email.attrs.get("value")
    if kirkes_form is not None:
        kirkes_email = kirkes_form.find("input", {'name': 'email'})
        kirkes_nick = kirkes_form.find("input", {'name': 'finna_nickname'})
        if kirkes_email is not None:
            if kirkes_email.has_attr("value"):
                user['kirkes_preferences']['email'] = kirkes_email.attrs.get("value")
        if kirkes_nick is not None:
            if kirkes_nick.has_attr("value"):
                user['kirkes_preferences']['nickname'] = kirkes_nick.attrs.get("value")
    return user


def getFines(html):
    pageContent = BeautifulSoup(html, 'html.parser')

    fines = {
        "currency": "€",
        "total_due": 0,
        "payable_due": 0,
        "fines": []
    }
    opd_element = pageContent.find("div", {'class': 'text-right online-payment-data'})
    if opd_element is not None:
        amount_opd = opd_element.find("span", {'class': 'amount'})
        if amount_opd is not None:
            price_search = re.search(price_regex, amount_opd.text)
            if price_search is not None:
                price_text = price_search.group(1)
                price_text = price_text.replace(",", ".")
                price_float = float(price_text)
                fines['payable_due'] = price_float

    fines_table = pageContent.find("table", {'class': 'table table-striped useraccount-table online-payment'})
    total_element = pageContent.find("td", {'class': 'total-balance'})
    if total_element is not None:
        amount_total = total_element.find("span", {'class': 'amount'})
        if amount_total is not None:
            price_search = re.search(price_regex, amount_total.text)
            if price_search is not None:
                price_text = price_search.group(1)
                price_text = price_text.replace(",", ".")
                price_float = float(price_text)
                fines['total_due'] = price_float
    if fines_table is not None:
        fine_items = fines_table.find_all("tr")
        for fine in fine_items:
            if fine.element_classes is None or "headers" not in fine.element_classes:
                fine_object = {

                }
                balance_elem = fine.find("td", {'class': 'balance'})
                date_elem = fine.find("td", {'class': 'hidden-xs'})
                if balance_elem is not None:
                    price_search = re.search(price_regex, balance_elem.text)
                    if price_search is not None:
                        price_text = price_search.group(1)
                        price_text = price_text.replace(",", ".")
                        price_float = float(price_text)
                        fine_object['price'] = price_float
                if date_elem is not None:
                    date_txt = date_elem.text
                    date_regex = re.search(expirationDateRegex, date_txt)
                    if date_regex is not None:
                        date_txt = date_regex.group(1)
                        date = datetime.datetime.strptime(date_txt,
                                                          "%d.%m.%Y").strftime("%Y/%m/%d")
                        fine_object['registration_date'] = date
                elements = fine.find_all('td')
                if len(elements) > 2:
                    desc_elem = elements[3]
                    fine_object['description'] = desc_elem.text.strip()
                if fine_object.get("price", None) is not None:
                    fines['fines'].append(fine_object)
    return fines
