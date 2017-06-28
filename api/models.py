import uuid
import math
from binascii import a2b_hex, b2a_hex
from datetime import datetime
from django.db import models
from .game import Moves, resolve_round, resolve_game
from django.utils import timezone
from api.locking import lock_factory
from django.contrib.postgres.fields import JSONField


class Client(models.Model):
    id = models.UUIDField(primary_key=True)
    secret = models.TextField(default="00")
    token = models.TextField(blank=True)
    energy = models.OneToOneField(to='Energy', blank=True, null=True)
    profile = models.ForeignKey(to='Contact', blank=True, null=True)
    contacts = models.ManyToManyField(to='Contact', related_name='friends')

    is_staff = models.BooleanField(default=False)
    is_bot = models.BooleanField(default=False)

    creation_date = models.DateTimeField(auto_now_add=True)

    @property
    def secret_bytes(self):
        return a2b_hex(self.secret)

    @secret_bytes.setter
    def secret_bytes(self, value):
        self.secret = b2a_hex(value)

    @property
    def contacts_by_name(self):
        return self.contacts.order_by('display_name')

    @property
    def stats(self):
        from django.db import connection

        with connection.cursor() as cur:
            cur.execute('''
                select count(rs.*), sum(rs.won), sum(rs.lost), sum(rs.draw)
                from (
                    select
                        (case when g1.winner_id = p1.id then 1 else 0 end) as won,
                        (case when g1.winner_id = p2.id then 1 else 0 end) as lost,
                        (case when g1.winner_id is null then 1 else 0 end) as draw
                    from api_game g1
                    join api_player p1 on p1.game_id = g1.id
                    join api_player p2 on p2.game_id = g1.id and p2.id != p1.id
                    where p1.client_id = %s and g1.status = 'C'
                ) as rs
            ''', [self.id])
            row = cur.fetchone()

        return {
            'played': row[0],
            'won': row[1] or 0,
            'lost': row[2] or 0,
            'draw': row[3] or 0
        }

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
                WHERE cl1.id = %s AND cl1.id != cl2.id
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
                WHERE cl1.id = %s AND cl1.id != cl2.id
            ) friends
            GROUP BY friends.id, friends.profile_id
        ''', [self.id, self.id])

    @property
    def invites(self):
        """
        Find contacts which are NOT a client.
        :return: Contacts which are NOT a client.
        """

        return Contact.objects.raw("""
            SELECT co1.*
            FROM api_client cl1
            JOIN api_client_contacts cc1 ON cc1.client_id = cl1.id
            JOIN api_contact co1 ON co1.id = cc1.contact_id
            JOIN api_rawcontact rc1 ON rc1.contact_id = co1.id
            JOIN api_data da1 ON da1.raw_contact_id = rc1.id AND da1.type = 'PHONE'
            WHERE cl1.id = %s and da1.value not in (
                select da2.value
                from api_client cl2
                join api_contact co2 ON cl2.profile_id = co2.id
                join api_rawcontact rc2 ON co2.id = rc2.contact_id
                join api_data da2 ON da2.raw_contact_id = rc2.id and da2.type = 'PHONE'
            )
            GROUP BY co1.id
        """, [self.id])

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


class Energy(models.Model):
    regen_rate = models.FloatField()  # in points per hour
    pool_size = models.IntegerField()

    @property
    def levels_by_time(self):
        return self.levels.order_by('-time')

    def _compute_current_level(self):
        last_level = self.levels.order_by('-time').first()
        if not last_level:
            new_level = self.levels.create(value=self.pool_size)
            return 0, math.floor(new_level.value), 0

        now = datetime.now(tz=last_level.time.tzinfo)
        delta = now - last_level.time
        hours = delta.total_seconds() / 3600.0
        level_inc = hours * self.regen_rate
        new_level_value = min(last_level.value + level_inc, self.pool_size)

        if (level_inc > 0 and new_level_value <= self.pool_size and hours >= 0.1) or level_inc >= 10 or hours >= 1:
            self.levels.create(value=new_level_value)

        return level_inc, new_level_value, hours

    @property
    def _lock_name(self):
        return "energy-{}".format(self.id)

    @property
    def current_level(self):
        with lock_factory.create_lock(self._lock_name):
            level_inc, new_level_value, hours = self._compute_current_level()

            return math.floor(new_level_value)

    def consume(self, amount):
        with lock_factory.create_lock(self._lock_name):
            level_int, new_level_value, hours = self._compute_current_level()

            consumed_value = new_level_value - amount
            if consumed_value >= 0:
                self.levels.create(value=consumed_value)
                return True
            else:
                return False


class EnergyLevel(models.Model):
    owner = models.ForeignKey(to='Energy', related_name='levels')
    time = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField()


class Notification(models.Model):
    client = models.ForeignKey(to='Client', related_name='notifications')
    template = models.ForeignKey(to='NotificationTemplate')
    when = models.DateTimeField(auto_now_add=True, editable=False)
    sent = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    title_args = JSONField(default=[])
    body_args = JSONField(default=[])
    data = JSONField(default={})


class NotificationTemplate(models.Model):
    id = models.CharField(max_length=256, primary_key=True)
    title_key = models.CharField(max_length=256)
    body_key = models.CharField(max_length=256)

    def __str__(self):
        return self.id


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
    game = models.ForeignKey(to='Game', on_delete=models.CASCADE)


class Game(models.Model):
    OPEN = 'O'
    CLOSED = 'C'
    STATUS = (
        (OPEN, 'Open'),
        (CLOSED, 'Closed')
    )

    rounds_num = models.IntegerField()
    status = models.CharField(max_length=1, default='O', choices=STATUS)
    winner = models.ForeignKey(to='Player', related_name='game_won', blank=True, null=True)
    date_started = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(blank=True, null=True)

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
    def has_bot(self):
        return self.player_set.filter(client__is_bot=True).count() > 0

    def resolve(self):
        if not self.over:
            return

        winner, _ = resolve_game([(r.number, r.winner_id) for r in self.rounds.all()])

        self.winner_id = winner
        self.status = Game.CLOSED
        self.date_ended = timezone.now()
        self.save()


class Round(models.Model):
    game = models.ForeignKey(to='Game', related_name='rounds', on_delete=models.CASCADE)
    winner = models.ForeignKey(to='Player', related_name='rounds_won', blank=True, null=True)
    number = models.SmallIntegerField(default=0)

    @property
    def players(self):
        return [move.player_id for move in self.move_set.all()]

    @property
    def complete(self):
        game_players = set(map(lambda player: player.id, self.game.player_set.all()))
        round_players = set(map(lambda move: move.player_id, self.move_set.all()))
        diff = game_players.symmetric_difference(round_players)
        return len(diff) == 0

    def resolve(self):
        winner, _ = resolve_round([(move.player_id, move.move) for move in self.move_set.all()])

        self.winner_id = winner
        self.save()

    class Meta:
        unique_together = ('game', 'number',)


class Move(models.Model):
    MOVES = (
        ('LIZ', 'Lizard'),
        ('SPO', 'Spock'),
        ('SIS', 'Scissors'),
        ('ROC', 'Rock'),
        ('PAP', 'Paper')
    )

    round = models.ForeignKey(to='Round', on_delete=models.CASCADE)
    player = models.ForeignKey(to='Player')

    move = models.CharField(max_length=3, choices=MOVES)

    @property
    def move_name(self):
        return Moves.NAMES[self.move]

    class Meta:
        unique_together = ('round', 'player',)
