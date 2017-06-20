from collections import defaultdict
import itertools


class Moves:
    class Move:
        def __init__(self, name, wins):
            self.name = name
            self.wins = wins

    ROCK = 'ROC'
    PAPER = 'PAP'
    SCISSORS = 'SIS'
    LIZARD = 'LIZ'
    SPOCK = 'SPO'
    MOVES = [ROCK, PAPER, SCISSORS, LIZARD, SPOCK]
    NAMES = {
        ROCK: 'Rock',
        PAPER: 'Paper',
        SCISSORS: 'Scissors',
        LIZARD: 'Lizard',
        SPOCK: 'Spock'
    }
    WINS = {
        ROCK: (SCISSORS, LIZARD),
        PAPER: (ROCK, SPOCK),
        SCISSORS: (PAPER, LIZARD),
        LIZARD: (PAPER, SPOCK),
        SPOCK: (ROCK, SCISSORS)
    }

    @staticmethod
    def resolve(move1, move2):
        assert move1 in Moves.MOVES
        assert move2 in Moves.MOVES

        if move1 == move2:
            return 0, 0
        elif move2 in Moves.WINS[move1]:
            return 1, -1  # move1 wins
        else:
            return -1, 1  # move2 wins


def sort_scores(scores):
    winners = sorted(scores.items(), key=lambda t: t[1], reverse=True)
    winners = itertools.groupby(winners, key=lambda t: t[1])
    return [(k, [p for p, s in v]) for k, v in winners]


def find_winner(winners, scores):
    # Check if there's a definitive winner
    if len(winners[0][1]) > 1:
        return None, scores
    else:
        return winners[0][1][0], scores.items()


def resolve_round(moves):
    scores = defaultdict(lambda: 0)
    for (player1, move1), (player2, move2) in itertools.combinations(moves, 2):
        score1, score2 = Moves.resolve(move1, move2)

        scores[player1] += score1
        scores[player2] += score2

    winners = sort_scores(scores)
    return find_winner(winners, scores)


def resolve_game(rounds):
    scores = defaultdict(lambda: 0)
    for num, winner in rounds:
        scores[winner] += 1

    winners = sort_scores(scores)
    return find_winner(winners, scores)


if __name__ == '__main__':
    import unittest

    class TestResolveRound(unittest.TestCase):

        def test_draw(self):
            moves = [(1, 'ROC'), (2, 'ROC')]
            winner, scores = resolve_round(moves)
            self.assertEqual(winner, None)

    unittest.main()
