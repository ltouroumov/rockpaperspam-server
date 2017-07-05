from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import permissions
from django.db.utils import IntegrityError
from .models import *
from api.firebase import FirebaseCloudMessaging
from api.signals import *
from api.game import perform_resolve
from backend import settings
import itertools
import os

fcm = FirebaseCloudMessaging(settings.GCM_SERVER_KEY)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request: Request):
    from api.serializers import ClientSerializer

    client_id = request.data['client_id']

    if Client.objects.filter(id=client_id).exists():
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={
            'error': 'Client already registered'
        })

    client = Client(id=client_id)
    client.secret_bytes = os.urandom(16)

    profile = Contact(display_name='You')
    profile.save()

    energy = Energy(regen_rate=1, pool_size=5)
    energy.save()

    try:
        client.profile_id = profile.id
        client.energy_id = energy.id
        client.save()
        return Response(status=status.HTTP_201_CREATED, data={
            'secret': client.secret,
            'client': ClientSerializer(client).data
        })
    except Exception as ex:
        import traceback
        traceback.print_exc()
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={
            'error': 'Register Error!',
            'message': str(ex)
        })


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

    print("old token:", client.token)
    client.token = data['token']
    print("new token:", client.token)

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


@api_view(['GET'])
def client_status(request: Request):
    from api.serializers import ClientSerializer

    client_id = request.user.id
    client = Client.objects.get(id=client_id)

    return Response(status=status.HTTP_200_OK, data=ClientSerializer(client).data)


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
                    ((True, b.id, b.profile) for b in Client.objects.filter(is_bot=True)),
                    ((False, i.id, i) for i in client.invites),
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

    try:
        from django.db import connection
        with connection.cursor() as cur:
            cur.execute('''
              SELECT count(g.*)
              FROM api_game g
              JOIN api_player p1 ON g.id = p1.game_id AND p1.client_id = %s
              JOIN api_player p2 ON g.id = p2.game_id AND p2.client_id = %s
              WHERE g.status = 'O'
            ''', [challenger.id, defender.id])

            row = cur.fetchone()
            number = row[0]

            if number > 0:
                print("Already challenging {}!".format(defender.id))
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'You are already playing against this user'})
    except Exception as ex:
        from traceback import print_exc
        print_exc()
        raise APIException()

    the_game = Game.objects.create(rounds_num=request.data['rounds'])
    the_game.player_set.create(client=challenger)
    the_game.player_set.create(client=defender)

    the_game.rounds.create(number=1)

    the_game.save()

    Notification.objects.create(client=challenger,
                                data={'action': 'startGame', 'id': the_game.id})

    Notification.objects.create(client=defender,
                                template_id='new_game',
                                body_args=[challenger.profile.display_name])

    on_game_start.send(sender='start', game_id=the_game.id)

    return Response(status=status.HTTP_201_CREATED, data={'id': the_game.id})


def process_resolve(round_complete, game_complete, the_game, the_round):
    if round_complete:
        if game_complete:
            if the_game.winner:
                resp = Response(status=status.HTTP_200_OK, data={'is_over': True, 'winner': the_game.winner.client.id})
            else:
                resp = Response(status=status.HTTP_200_OK, data={'is_over': True, 'winner': None})

            for player in the_game.player_set.all():
                Notification.objects.create(client_id=player.client_id,
                                            template_id='game_over',
                                            data={'action': 'gameOver', 'id': the_game.id})

        else:
            for player in the_game.player_set.all():
                Notification.objects.create(client_id=player.client_id,
                                            template_id='new_round',
                                            data={'action': 'newRound', 'id': the_game.id})

            resp = Response(status=status.HTTP_200_OK, data={'is_over': False})
    else:
        resp = Response(status=status.HTTP_200_OK, data={'is_over': False})

    return resp


@api_view(['POST'])
def play(request: Request, pk, rid):
    from api.locking import lock_factory

    only_resolve = request.GET.get('resolve', 'false') == 'true'

    try:
        the_game = Game.objects.get(id=pk)
    except Game.DoesNotExist:
        raise GameException('Game not found')

    if the_game.status != Game.OPEN:
        raise GameException('Game closed')

    try:
        the_round = the_game.rounds.get(number=rid)
    except Round.DoesNotExist:
        raise GameException('Invalid round number')

    with lock_factory.create_lock("play-{}-{}".format(the_game.id, the_round.id)):
        if not only_resolve:
            try:
                player = the_game.player_set.get(client_id=request.data['from'])
            except Player.DoesNotExist:
                raise GameException('Invalid player')

            if player.client.energy.consume(1):
                try:
                    the_round.move_set.create(player=player, move=request.data['move'])
                except IntegrityError:
                    raise GameException('You\'ve already played this round')
            else:
                raise GameException(detail='No energy left', code='no-energy')

        round_complete, game_complete = perform_resolve(the_game, the_round)
        resp = process_resolve(round_complete, game_complete, the_game, the_round)

        if not only_resolve:
            on_game_play.send(sender='play', game_id=the_game.id, round_id=the_round.id)

        return resp


@api_view(['POST'])
def notifications_ack(request: Request):

    try:
        notification_id = request.data['notification_id']
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Missing 'notification_id' in body"})

    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Notification id does not exist"})

    if notification.client_id != request.user.id:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Cannot ack a notification not sent to you"})

    notification.read = True
    notification.save()

    return Response(status=status.HTTP_200_OK)
