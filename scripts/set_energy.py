from api.models import *
from argparse import ArgumentParser


def run(*varargs):
    parser = ArgumentParser()
    parser.add_argument('client')
    parser.add_argument('value', type=int)

    args = parser.parse_args(varargs)

    client = Client.objects.get(id=args.client)
    energy = client.energy

    energy.levels.create(value=args.value)

    print("Set energy of {} ({}) at {}".format(client.profile.display_name, client.id, args.value))

