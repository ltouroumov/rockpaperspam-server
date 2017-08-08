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


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'display_name')


class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = ('type', 'value')


class RawContactSerializer(serializers.ModelSerializer):
    data = DataSerializer(many=True)

    class Meta:
        model = RawContact
        fields = ('id', 'contact_type', 'contact_name', 'data')


class EnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Energy
        fields = ('pool_size', 'regen_rate', 'current_level')


class ClientSerializer(serializers.ModelSerializer):
    profile = ContactSerializer()
    energy = EnergySerializer()

    class Meta:
        model = Client
        fields = ('id', 'profile', 'stats', 'energy')
