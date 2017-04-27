import enum

from django.db import models
from datetime import datetime
import uuid


class Client(models.Model):
    id = models.UUIDField(primary_key=True)
    token = models.TextField(blank=True)
    profile = models.ForeignKey(to='Contact', blank=True, null=True)
    contacts = models.ManyToManyField(to='Contact', related_name='friends')

    @property
    def contacts_by_name(self):
        return self.contacts.order_by('display_name')

    @property
    def friends(self):
        """
        The SQL query from hell
        
        Since contact-book friendships can be non-reflexive, we search both:
        "has friends in my contacts" and "is in contacts of friend"
        
        :return: All the friends
        """
        return Client.objects.raw('''
            SELECT friends.id, friends.profile_id, array_agg(friends.side) as sides
            FROM (
                SELECT 'L' as side, cl2.*
                FROM api_client cl1
                JOIN api_client_contacts cc1 ON cc1.client_id = cl1.id
                JOIN api_contact co1 ON co1.id = cc1.contact_id
                JOIN api_rawcontact rc1 ON rc1.contact_id = co1.id
                JOIN api_data da1 ON da1.raw_contact_id = rc1.id AND da1.type = 'PHONE'
                JOIN api_data da2 ON da2.value = da1.value
                JOIN api_rawcontact rc2 ON rc2.id = da2.raw_contact_id
                JOIN api_contact co2 ON co2.id = rc2.contact_id
                JOIN api_client cl2 ON cl2.profile_id = co2.id
                WHERE cl1.id = %s
                UNION 
                SELECT 'R' as side, cl2.*
                FROM api_client cl1
                JOIN api_contact co1 ON co1.id = cl1.profile_id
                JOIN api_rawcontact rc1 ON rc1.contact_id = co1.id
                JOIN api_data da1 ON da1.raw_contact_id = rc1.id AND da1.type = 'PHONE'
                JOIN api_data da2 ON da1.value = da2.value
                JOIN api_rawcontact rc2 ON rc2.id = da2.raw_contact_id
                JOIN api_contact co2 ON co2.id = rc2.contact_id
                JOIN api_client_contacts cc2 ON cc2.contact_id = co2.id
                JOIN api_client cl2 ON cl2.id = cc2.client_id
                WHERE cl1.id = %s
            ) friends
            GROUP BY friends.id, friends.profile_id
        ''', [self.id, self.id])

    @property
    def games(self):
        return Game.objects.filter(player__client=self)

    def __str__(self):
        return str.format("Client({0.id}):{0.profile}", self)


class Sync(models.Model):
    client = models.ForeignKey(to='Client')
    date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return "Sync({0.client_id}, {0.date})".format(self)


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact_id = models.BigIntegerField(default=0)
    contact_key = models.CharField(max_length=1024, default="0")
    display_name = models.CharField(max_length=1024)

    @property
    def key(self):
        return "%s/%d" % (self.contact_key, self.contact_id)

    @property
    def data(self):
        return Data.objects.filter(raw_contact__contact__id=self.id)

    def data_for_tags(self, tags):
        return Data.objects.filter(type__in=tags, raw_contact__contact__id=self.id)

    def __str__(self):
        return str.format("Contact({0.id}, {0.contact_id}/{0.contact_key}, {0.display_name})", self)


class RawContact(models.Model):
    contact = models.ForeignKey(to='Contact', related_name='raw_contacts')

    contact_type = models.CharField(max_length=256)
    contact_name = models.CharField(max_length=512, blank=True)

    def data_for_tags(self, tags):
        return self.data.filter(type__in=tags)

    def __str__(self):
        return str.format("RawContact({0.id}, {0.contact_type}, {0.contact_name})", self)


class Data(models.Model):
    TYPES = (
        ('NAME', 'Name'),
        ('PHONE', 'Phone Number'),
        ('EMAIL', 'Email Address'),
        ('WHATSAPP', 'Whatsapp ID'),
    )

    raw_contact = models.ForeignKey(to='RawContact', related_name='data')

    type = models.CharField(max_length=32, choices=TYPES)
    # Canonical Phone Number (ex. +41793571289)
    value = models.CharField(max_length=1024)

    def __str__(self):
        return self.value


class Player(models.Model):
    client = models.ForeignKey(to='Client')
    game = models.ForeignKey(to='Game')


class Game(models.Model):
    OPEN = 'O'
    CLOSED = 'C'
    STATUS = (
        (OPEN, 'Open'),
        (CLOSED, 'Closed')
    )

    rounds_num = models.IntegerField()
    status = models.CharField(max_length=1, default='O', choices=STATUS)

    @property
    def rounds_ordered(self):
        return self.rounds.order_by('number')

    @property
    def current_round(self):
        return self.rounds_ordered.last().number

    @property
    def over(self):
        return self.rounds.count() == self.rounds_num

    @property
    def winner(self):
        return "???"


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


class Round(models.Model):
    game = models.ForeignKey(to='Game', related_name='rounds')
    winner = models.ForeignKey(to='Player', blank=True, null=True)
    number = models.SmallIntegerField(default=0)

    @property
    def complete(self):
        game_players = set(map(lambda player: player.id, self.game.player_set.all()))
        round_players = set(map(lambda move: move.player_id, self.move_set.all()))
        diff = game_players.symmetric_difference(round_players)
        return len(diff) == 0

    def resolve(self):
        import itertools
        print('resolving round ...')
        moves = self.move_set.all()
        if len(moves) > 2:
            raise Exception("Too many moves for this round")

        for move1, move2 in itertools.combinations(moves, 2):
            if move1.move == move2.move:
                print("Draw -_-")
                self.winner = None
            else:
                print(move1.move, "VS", move2.move)
                if move2.move in Moves.WINS[move1.move]:
                    self.winner = move1.player
                else:
                    self.winner = move2.player

        self.save()

    class Meta:
        unique_together = ('game', 'number',)


class Move(models.Model):
    MOVES = tuple(Moves.NAMES.items())

    round = models.ForeignKey(to='Round')
    player = models.ForeignKey(to='Player')

    move = models.CharField(max_length=3, choices=MOVES)

    @property
    def move_name(self):
        return Moves.NAMES[self.move]

    class Meta:
        unique_together = ('round', 'player',)
