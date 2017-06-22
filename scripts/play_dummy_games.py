import itertools
import random
from api.models import *

MOVES = ('ROC', 'PAP', 'SIS', 'LIZ', 'SPO')


def run(*args):
    clients = Client.objects.raw("select * from api_client where id::VARCHAR like %s", ['ffffffff-%'])
    pairs = tuple(itertools.combinations(clients, 2))

    for c1, c2 in pairs:
        rounds = (2*random.randint(1, 3))+1

        the_game = Game.objects.create(rounds_num=rounds)
        p1 = the_game.player_set.create(client=c1)
        p2 = the_game.player_set.create(client=c2)

        the_game.save()

        print("[+] Game {:d} ({:d} rounds)".format(the_game.id, the_game.rounds_num))
        for rnd in range(1, rounds+1):
            print("    [+] Round", rnd)
            round = the_game.rounds.create(number=rnd)

            p1_move = random.choice(MOVES)
            p2_move = random.choice(MOVES)

            for p, m in ((p1, p1_move), (p2, p2_move)):
                round.move_set.create(player=p, move=m)

            round.resolve()

        the_game.resolve()
        print("[+] Game {}: {} winner: {}".format(the_game.id, the_game.status, the_game.winner_id))
