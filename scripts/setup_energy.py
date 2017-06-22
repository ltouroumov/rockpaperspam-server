from api.models import *


def run(*args):
    clients = Client.objects.all()

    for client in clients:
        if not client.energy_id:
            client.energy = Energy.objects.create(pool_size=5, regen_rate=1)
            client.energy.levels.create(value=5)

        client.save()
