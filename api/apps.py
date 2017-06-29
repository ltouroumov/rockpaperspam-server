from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        super().ready()

        from django.db.models import signals as db_signals
        from api import signals as app_signals
        from api import bots

        app_signals.on_game_play.connect(receiver=bots.on_game_play,
                                         dispatch_uid='bots_on_game_play')

        db_signals.pre_save.connect(receiver=bots.pre_notification_saved,
                                    sender='api.Notification',
                                    dispatch_uid='bots_pre_notification_saved')

        db_signals.post_save.connect(receiver=bots.post_notification_saved,
                                     sender='api.Notification',
                                     dispatch_uid='bots_post_notification_saved')
