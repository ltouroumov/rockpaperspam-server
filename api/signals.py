from django.dispatch import Signal

on_game_start = Signal(providing_args=['game_id'])
on_game_play = Signal(providing_args=['game_id', 'round_id'])
