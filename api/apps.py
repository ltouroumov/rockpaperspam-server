from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        super().ready()

        from api import signals
        from api import bots

        signals.on_game_play.connect(bots.on_game_play, dispatch_uid='bots_on_game_play')
