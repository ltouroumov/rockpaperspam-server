from api.models import Client
from tabulate import tabulate


def make_table_row(client):
    stats = client.stats

    return client.id, stats['played'], stats['won'], stats['lost'], stats['draw']


def run(*args):
    clients = Client.objects.order_by('profile__display_name')

    data = list(map(make_table_row, clients))
    print(tabulate(headers=['Client', 'Played', 'Victories', 'Defeats', 'Draws'], tabular_data=data))
