from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import permissions
from .models import *


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def sync(request: Request):
    """
    Synchronizes contact list for a client

    JSON Structure:

    {
        "client_id": <client-id>,
        "token": <firebase-token>,
        "info": {
            "profile": {
                "name": "Jane Doe",
                "emails": [
                    "jane.doe@gmail.com"
                ],
                "phones": [
                    "+41791234567"
                ],
                "whatsApp": "41791234567@s.whatsapp.net"
            },
            "friends": [
                {
                    "name": "John Doe",
                    "emails": [
                        "john.doe@gmail.com"
                    ],
                    "phone": [
                        "+41799876543"
                    ],
                    "whatsApp": "41799876543@s.whatsapp.net"
                },
                ...
            ]
        }
    }

    :param request:
    :return:
    """

    data = request.data
    profile_json = data['profile']

    try:
        client = Client.objects.get(id=data['client_id'])
        profile = client.profile
    except Client.DoesNotExist:
        client = Client(id=data['client_id'])
        profile = Contact.objects.create()
        client.profile_id = profile.id

    client.token = data['token']

    profile.contact_id = profile_json['id']
    profile.contact_key = profile_json['key']
    profile.display_name = profile_json['name']
    profile.save()
    client.save()

    for data_json in profile_json['data']:
        profile.data.get_or_create(type=data_json['type'], value=data_json['value'])

    for friend_json in data['friends']:
        friend, created = client.friends.get_or_create(
            contact_id=friend_json['id'],
            contact_key=friend_json['key'],
            display_name=friend_json['name']
        )
        for data_json in friend_json['data']:
            friend.data.get_or_create(
                type=data_json['type'],
                value=data_json['value']
            )
        friend.save()

    return Response(status=status.HTTP_200_OK)
