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

    client.sync_set.create(date=datetime.now())

    for raw_json in profile_json['rawContacts']:
        raw_contact, created = profile.raw_contacts.get_or_create(contact_type=raw_json['type'])
        raw_contact.contact_name = raw_json['name']

        for data_json in raw_json['data']:
            raw_contact.data.get_or_create(type=data_json['type'], value=data_json['value'])

        raw_contact.save()

    old_friends = {friend.key: friend for friend in client.friends.all()}

    # Add or update friends
    for friend_json in data['friends']:
        friend, created = client.friends.get_or_create(
            contact_id=friend_json['id'],
            contact_key=friend_json['key'],
            display_name=friend_json['name']
        )
        # Remove from old_friends if exists
        if friend.key in old_friends:
            del old_friends[friend.key]

        for raw_json in friend_json['rawContacts']:
            raw_contact, created = friend.raw_contacts.get_or_create(contact_type=raw_json['type'])
            raw_contact.contact_name = raw_json['name']

            for data_json in raw_json['data']:
                raw_contact.data.get_or_create(type=data_json['type'], value=data_json['value'])

            raw_contact.save()

        friend.save()

    # Remove old friends :(
    for old_friend in old_friends.values():
        old_friend.delete()

    return Response(status=status.HTTP_200_OK)
