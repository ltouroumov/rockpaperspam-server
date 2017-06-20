from .models import *
from rest_framework import serializers


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ('number', 'winner_id', 'players')


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'client_id',)


class GameSerializer(serializers.ModelSerializer):
    winner = serializers.SlugRelatedField(read_only=True, slug_field='id')
    rounds = RoundSerializer(many=True)
    player_set = PlayerSerializer(many=True)

    class Meta:
        model = Game
        fields = ('id', 'status', 'date_started', 'date_ended', 'player_set', 'rounds_num', 'rounds', 'current_round', 'winner')
