from .models import *
from rest_framework import serializers


class GameSerializer(serializers.ModelSerializer):
    winner = serializers.SlugRelatedField(read_only=True, slug_field='client_id')

    class Meta:
        model = Game
        fields = ('id', 'status', 'rounds_num', 'current_round', 'winner')
