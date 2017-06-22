import itertools
from uuid import UUID
import hashlib
from unidecode import unidecode
from api.models import *

NAMES = [
    "Adélie Trudeau",
    "Sabrina Sadoul",
    "Emilie Moineau",
    "Ninon Jacquinot",
    "Laurine Gardet",
    "Ségolène Renaudin",
    "Sylvie Marchal",
    "Blanche Magnier",
    "Sylvie Asselineau",
    "Marcelle Girault",
    "Justin Rochefort",
    "Marius Bombelles",
    "Abel Gicquel",
    "Francis Lucy",
    "Josselin Bacque",
    "Kévin Gauthier",
    "Frédéric Vannier",
    "Grégoire Carré",
    "Armel Abbadie",
    "Gustave Descombes",
]


def get_num(byt, mod):
    return abs(int.from_bytes(byt, byteorder='big') % mod)


def gen_profile(user_id, full_name):
    name_hash = hashlib.sha1(full_name.encode('utf-8')).digest()

    norm_name = unidecode(full_name)
    email = norm_name.lower().replace(' ', '.') + "@gmail.com"
    phone = "+4179%03d%02d%02d" % (get_num(name_hash[0:4], 1000), get_num(name_hash[4:6], 100), get_num(name_hash[6:8], 100))
    return user_id, {
        'hash': name_hash,
        'client_id': UUID(bytes=b'\xff\xff\xff\xff' + name_hash[0:12]),
        'display_name': full_name,
        'email': email,
        'acct_id': user_id,
        'phone': phone
    }


def make_friend(client, person):
    contact = client.contacts.create(contact_id=person['acct_id'], contact_key='dummy',
                                     display_name=person['display_name'])
    contact_raw = contact.raw_contacts.create(contact_type='com.dummy', contact_name=person['acct_id'])
    contact_raw.data.create(type='NAME', value=person['display_name'])
    contact_raw.data.create(type='PHONE', value=person['phone'])
    contact_raw.data.create(type='EMAIL', value=person['email'])

    return contact


def run(*args):
    peoples = dict(itertools.starmap(gen_profile, enumerate(NAMES)))

    for person in peoples.values():
        friends = [peoples[b % len(peoples)] for b in person['hash'][0:8]]

        qs = Client.objects.filter(id=person['client_id'])
        if qs.exists():
            print("[\u26A0] Deleted", person['client_id'])
            qs.delete()

        client = Client(id=person['client_id'])

        profile = Contact.objects.create(contact_id=person['acct_id'], contact_key='profile', display_name=person['display_name'])
        profile_raw = profile.raw_contacts.create(contact_type='com.android.profile', contact_name='Profile')
        profile_raw.data.create(type='NAME', value=person['display_name'])
        profile_raw.data.create(type='PHONE', value=person['phone'])
        profile_raw.data.create(type='EMAIL', value=person['email'])
        client.profile = profile

        client.energy = Energy(pool_size=50, regen_rate=5)
        client.energy.save()

        client.save()
        print("[\u2713] Inserted {} ({})".format(person['display_name'], client.id))

        client.contacts.all().delete()
        for friend in friends:
            contact = make_friend(client, friend)
            print("    [\u2713] Friend {} ({})".format(friend['display_name'], contact.id))