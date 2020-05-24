# -*- coding: utf-8 -*-

#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

from __future__ import unicode_literals

from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import *
from rest_framework.views import exception_handler

from openKirkesAuth.backend.auth import new_token
from openKirkesConnector.web_client import *
from openKirkesConverter.converter import statuses, library_types


# Custom Error handler to make it fit with rest of the API
def custom_exception_handler(exc, context):
    return generateErrorResponse(ErrorResult(exc))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def loans(request):
    lang = request.query_params.get('lang', "en-gb")
    loans = getKirkesClientFromRequest(request, lang).loans()
    if loans.is_error():
        return generateErrorResponse(loans)
    content = {
        'loans': loans.get_loans()
    }
    return generateResponse(content)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def holds(request):
    lang = request.query_params.get('lang', "en-gb")
    holds = getKirkesClientFromRequest(request, lang).holds()
    if holds.is_error():
        return generateErrorResponse(holds)
    content = {
        'statuses': statuses,
        'holds': holds.get_holds()
    }
    return generateResponse(content)


@api_view(['GET'])
@permission_classes([])
def lib_info(request):
    lang = request.query_params.get('lang', "en-gb")
    libraries = KirkesClient(None, lang).lib_info()
    if libraries.is_error():
        return generateErrorResponse(libraries)
    content = {
        'types': library_types,
        'libraries': libraries.get_libs(),
    }
    return generateResponse(content)

@api_view(['GET'])
@permission_classes([])
def search(request):
    lang = request.query_params.get('lang', "en-gb")
    query = request.query_params.get('search', None)
    page = request.query_params.get('page', '1')
    if query is None:
        return generateErrorResponse(ErrorResult('Search query is missing!'))
    result = KirkesClient(None, lang).search(query, page)
    if result.is_error():
        return generateErrorResponse(result)
    content = {
        'count': result.get_count(),
        'results': result.get_results(),
    }
    return generateResponse(content)


@api_view(['GET'])
@permission_classes([])
def details(request):
    lang = request.query_params.get('lang', "en-gb")
    query = request.query_params.get('id', None)
    if query is None:
        return generateErrorResponse(ErrorResult('Resource ID is missing!'))
    result = KirkesClient(None, lang).resource_details(query)
    if result.is_error():
        return generateErrorResponse(result)
    return generateResponse({'details': result.get_details()})

@api_view(['GET'])
@permission_classes([])
def details_raw(request):
    lang = request.query_params.get('lang', "en-gb")
    query = request.query_params.get('id', None)
    if query is None:
        return generateErrorResponse(ErrorResult('Resource ID is missing!'))
    result = KirkesClient(None, lang).raw_resource_details(query)
    if result.is_error():
        return generateErrorResponse(result)
    return generateResponse({'details_raw': result.get_details()})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pickupLocations(request):
    lang = request.query_params.get('lang', "en-gb")
    id = request.query_params.get("id", None)
    if id is None:
        return generateError("Query parameter 'id' is missing")
    locations = getKirkesClientFromRequest(request, lang).pickupLocations(id)
    if locations.is_error():
        return generateErrorResponse(locations)
    content = {
        'pickup_locations': locations.get_locations(),
        'default_location': locations.get_default(),
        'details': locations.get_details()
    }
    return generateResponse(content)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def changePickupLocation(request):
    lang = request.query_params.get('lang', "en-gb")
    locationId = request.query_params.get("locationId", None)
    actionId = request.query_params.get("actionId", None)
    if locationId is None:
        return generateError("Query parameter 'locationId' is missing")
    if actionId is None:
        return generateError("Query parameter 'actionId' is missing")
    locations = getKirkesClientFromRequest(request, lang).changePickupLocation(actionId, locationId)
    if locations.is_error():
        return generateErrorResponse(locations)
    content = {}
    return generateResponse(content)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fines(request):
    lang = request.query_params.get('lang', "en-gb")
    fines = getKirkesClientFromRequest(request, lang).getFines()
    if fines.is_error():
        return generateErrorResponse(fines)
    content = {
        'fine_details': fines.get_Fees()
    }
    return generateResponse(content)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_details(request):
    lang = request.query_params.get('lang', "en-gb")
    fines = getKirkesClientFromRequest(request, lang).getAccountDetails()
    if fines.is_error():
        return generateErrorResponse(fines)
    content = {
        'account': fines.get_user_details()
    }
    return generateResponse(content)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changeDefaultPickupLocation(request):
    lang = request.data.get('lang', "en-gb")
    locationId = request.data.get("locationId", None)
    if locationId is None:
        return generateError("Query parameter 'locationId' is missing")
    locations = getKirkesClientFromRequest(request, lang).changeDefaultPickupLocation(locationId)
    if locations.is_error():
        return generateErrorResponse(locations)
    content = {}
    return generateResponse(content)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDefaultLocation(request):
    lang = request.data.get('lang', "en-gb")
    location = getKirkesClientFromRequest(request, lang).getDefaultPickupLocation()
    if location.is_error():
        return generateErrorResponse(location)
    content = {
        'default_location': location.get_location()
    }
    return generateResponse(content)


def getKirkesClientFromRequest(request, language="en-gb"):
    enc_key = request.user.encryption_key
    authObject = request.user.getAuthenticationObject(enc_key)
    return KirkesClient(authObject, language, request.user)


@api_view(['POST'])
@permission_classes([])
def login(request):
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    language = request.data.get('lang', "en-gb")
    if username is None:
        return generateError('Username is missing!')
    if password is None:
        return generateError('Password is missing!')

    if request.user.is_anonymous and not request.user.is_authenticated:
        login_result = KirkesClient(None, language).login(username, password, True)
        if login_result.is_error():
            return generateErrorResponse(login_result)
        else:
            token = new_token(login_result.get_session(), username, password)
            return generateResponse({'token': token, 'user': login_result.get_user_details()})
    else:
        return generateError("You're already logged in")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def renew_loan(request):
    lang = request.data.get('lang', "en-gb")
    renew_id = request.data.get("renew_id", None)
    if renew_id is None:
        return generateError("POST parameter 'renew_id' is missing")
    renewResult = getKirkesClientFromRequest(request, lang).renew_loan(renew_id)
    if renewResult.is_error():
        return generateErrorResponse(renewResult)
    content = {
        'message': renewResult.get_message()
    }
    return generateResponse(content)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hold(request):
    lang = request.data.get('lang', "en-gb")
    res_id = request.data.get("id", None)
    type = request.data.get("type", None)
    location = request.data.get("location", None)
    if res_id is None:
        return generateError("POST parameter 'id' is missing")
    if type is None:
        return generateError("POST parameter 'type' is missing")
    if location is None:
        return generateError("POST parameter 'location' is missing")
    renewResult = getKirkesClientFromRequest(request, lang).hold(res_id, type, location)
    if renewResult.is_error():
        return generateErrorResponse(renewResult)
    return generateResponse({})


def generateErrorResponse(error_result):
    return generateError(str(error_result.get_exception()))


def generateError(cause):
    base = baseResponse()
    base.update({'cause': cause})
    return Response(base)


def generateResponse(data):
    base = baseResponse(True)
    base.update(data)
    return Response(base)


def baseResponse(status=False):
    return {
        'status': status
    }
