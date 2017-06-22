from api.models import *
from argparse import ArgumentParser


def run(*varargs):
    parser = ArgumentParser()
    parser.add_argument('client')
    parser.add_argument('regen_rate', type=float)
    parser.add_argument('pool_size', type=int)

    args = parser.parse_args(varargs)

    client = Client.objects.get(id=args.client)
    energy = client.energy

    energy.regen_rate = args.regen_rate
    energy.pool_size = args.pool_size
    energy.save()

    print("Set parameters of {} to regen_rate = {}, pool_size = {}".format(client.profile.display_name, energy.regen_rate, energy.pool_size))
