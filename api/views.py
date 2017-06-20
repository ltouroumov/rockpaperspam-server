from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import permissions
from django.db.utils import IntegrityError
from .models import *
from api.firebase import FirebaseCloudMessaging
from backend import settings
import itertools
from pprint import pprint
import os
import logging

logger = logging.getLogger(__name__)
fcm = FirebaseCloudMessaging(settings.GCM_SERVER_KEY)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request: Request):
    pprint(request.data)

    client_id = request.data['client_id']

    client = Client(id=client_id)
    client.profile = Contact()
    client.secret_bytes = os.urandom(16)

    try:
        client.profile.save()
        client.save()
        return Response(status=status.HTTP_201_CREATED, data={
            'secret': client.secret
        })
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
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

    old_friends = {friend.key: friend for friend in client.contacts.all()}
    friends_count_before = len(old_friends)
    created_friends = 0
    updated_friends = 0

    # Add or update friends
    for friend_json in data['friends']:
        friend, created = client.contacts.get_or_create(
            contact_id=friend_json['id'],
            contact_key=friend_json['key'],
            display_name=friend_json['name']
        )

        if created:
            created_friends += 1
            print("created", friend.key)
        else:
            updated_friends += 1
            print("updated", friend.key)

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

    deleted_friends = len(old_friends)

    # Remove old friends :(
    for old_friend in old_friends.values():
        print("deleted", old_friend.key)
        client.contacts.remove(old_friend)
        old_friend.delete()

    friends_count_after = client.contacts.count()

    return Response(status=status.HTTP_200_OK, data={
        'client_id': client.id,
        'friends_count_before': friends_count_before,
        'friends_count_after': friends_count_after,
        'created_friends': created_friends,
        'deleted_friends': deleted_friends,
        'updated_friends': updated_friends,
    })


def build_profile(ftype, id, profile):
    return {
        'id': id,
        'is_client': ftype,
        'display_name': profile.display_name
    }


@api_view(['GET'])
def profile(request: Request):
    client_id = request.GET.get('of')
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        from rest_framework.exceptions import NotFound
        raise NotFound()

    return Response(status=status.HTTP_200_OK, data=build_profile(True, client.id, client.profile))


@api_view(['GET'])
def friends(request: Request):
    client_id = request.user.id

    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        from rest_framework.exceptions import NotFound
        raise NotFound()

    friends_json = {
        'client': {'display_name': client.profile.display_name, 'id': client.id},
        'friends': list(
            itertools.starmap(
                build_profile,
                itertools.chain(
                    ((True, f.id, f.profile) for f in client.friends),
                    ((False, i.id, i) for i in client.invites)
                )
            )
        )
    }

    return Response(status=status.HTTP_200_OK, data=friends_json)


class GameException(APIException):
    status_code = 400


@api_view(['GET'])
def games(request: Request):
    from api.serializers import GameSerializer

    client_id = request.user.id

    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        raise APIException("Client does not exist")

    game_filter = request.GET.get('status', 'any')
    games = Game.objects.filter(player__client=client).order_by('-date_started' if game_filter == 'O' else '-date_ended')
    if game_filter != 'any':
        games = games.filter(status=game_filter)

    return Response(status=status.HTTP_200_OK, data=map(lambda game: GameSerializer(game).data, games))


@api_view(['GET'])
def game(request: Request, pk):
    from api.serializers import GameSerializer

    obj = Game.objects.get(id=pk)
    return Response(status=status.HTTP_200_OK, data=GameSerializer(obj).data)


@api_view(['POST'])
def start(request: Request):
    challenger = request.data['challenger']
    defender = request.data['defender']

    print("challenger = {}, defender = {}, user = {}".format(challenger, defender, request.user.id))

    if challenger != str(request.user.id):
        print("challenger != user")
        raise APIException('Challenger must be authenticated user')

    try:
        challenger = Client.objects.get(id=challenger)
    except Client.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Could not find challenger'})

    try:
        defender = Client.objects.get(id=defender)
    except Client.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Could not find defender'})

    if 'rounds' not in request.data:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Missing number of rounds'})

    the_game = Game.objects.create(rounds_num=request.data['rounds'])
    the_game.player_set.create(client=challenger)
    the_game.player_set.create(client=defender)

    the_game.rounds.create(number=1)

    the_game.save()

    fcm.send(to=[challenger.token, defender.token],
             payload={
                 'data': {
                    'action': 'startGame',
                    'id': the_game.id
                 }
             },
             multicast=True)

    return Response(status=status.HTTP_201_CREATED, data={'id': the_game.id})


@api_view(['POST'])
def play(request: Request, pk, rid):

    only_resolve = request.GET.get('resolve', 'false') == 'true'

    try:
        the_game = Game.objects.get(id=pk)
    except Game.DoesNotExist:
        raise GameException('Game not found')

    if the_game.status != Game.OPEN:
        raise GameException('Game closed')

    try:
        cur_round = the_game.rounds.get(number=rid)
    except Round.DoesNotExist:
        raise GameException('Invalid round number')

    if not only_resolve:
        try:
            player = the_game.player_set.get(client_id=request.data['from'])
        except Player.DoesNotExist:
            raise GameException('Invalid player')

        try:
            cur_round.move_set.create(player=player, move=request.data['move'])
        except IntegrityError:
            raise GameException('You\'ve already played this round')

    if cur_round.complete:
        cur_round.resolve()
        if the_game.over:
            print("Game is over :)")
            the_game.resolve()
            if the_game.winner:
                resp = Response(status=status.HTTP_200_OK, data={'is_over': True, 'winner': the_game.winner.client.id})
            else:
                resp = Response(status=status.HTTP_200_OK, data={'is_over': True, 'winner': None})

            fcm.send(to=list(map(lambda p: p.client.token, the_game.player_set.all())),
                     payload={
                         'data': {
                             'action': 'gameOver',
                             'id': the_game.id
                         }
                     },
                     multicast=True)

            return resp
        else:
            print("Moving on to next round")
            next_round = the_game.rounds.create(number=cur_round.number+1)

            fcm.send(to=list(map(lambda p: p.client.token, the_game.player_set.all())),
                     payload={
                         'data': {
                             'action': 'newRound',
                             'id': the_game.id
                         }
                     },
                     multicast=True)

            return Response(status=status.HTTP_200_OK, data={'is_over': False, 'next_round': next_round.number})
    elif only_resolve:
        return APIException('Incomplete round')
    else:
        return Response(status=status.HTTP_200_OK, data={'is_over': False})
