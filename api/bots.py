from random import choice

from api.firebase import FirebaseCloudMessaging
from api.game import Moves, perform_resolve
from api.models import *
from api.views import process_resolve
from rps_cnc import settings

fcm = FirebaseCloudMessaging(settings.GCM_SERVER_KEY)


def on_game_play(sender, game_id, round_id, **kwargs):
    print("BOT on_game_play", game_id, round_id)

    the_game = Game.objects.get(id=game_id)

    if the_game.has_bot:
        the_round = the_game.rounds.get(id=round_id)
        the_bot = the_game.player_set.get(client__is_bot=True)

        bot_move = choice(Moves.MOVES)
        print("Bot Playing", bot_move)

        the_round.move_set.create(player=the_bot, move=bot_move)

        round_complete, game_complete = perform_resolve(the_game, the_round)
        process_resolve(round_complete, game_complete, the_game, the_round)


def pre_notification_saved(sender, **kwargs):
    notification = kwargs.pop('instance', None)
    client = notification.client

    if not client.token:
        print("Client has no token")
        notification.sent = True
        notification.read = True


def post_notification_saved(sender, **kwargs):
    notification = kwargs.pop('instance', None)
    client = notification.client
    print("Notification {} saved".format(notification.id))
    if notification.sent or not client.token:
        return

    payload = {}
    payload['data'] = {'notification_id': notification.id}
    payload['data'].update(notification.data)

    if notification.template_id:
        template = notification.template
        payload['notification'] = template.payload()
        payload['notification'].update(notification.payload())

    print("to:", repr(client.token))
    print("payload:", repr(payload))

    fcm.send(to=client.token,
             payload=payload)

    notification.sent = True
    notification.save()
