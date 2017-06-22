from api.models import *
from api.game import Moves, perform_resolve
from api.views import process_resolve
from random import choice


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
