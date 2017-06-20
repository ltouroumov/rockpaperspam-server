from rest_framework import authentication
from rest_framework import exceptions
from .models import Client
import re
import hmac
import hashlib
from binascii import a2b_hex


class ClientUser:
    def __init__(self, client):
        self.client = client

    @property
    def id(self):
        return self.client.id

    @property
    def username(self):
        return self.client.id

    @property
    def is_staff(self):
        return False

    @property
    def is_authenticated(self):
        return True


class ClientAuthentication(authentication.BaseAuthentication):
    TOKEN_RX = re.compile(r'^Client (?P<cid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}):(?P<seed>[a-f0-9]{16}):(?P<token>[a-f0-9]{64})$', re.IGNORECASE)

    @staticmethod
    def compute_hash(client_id, seed, secret):
        return hmac.new(secret, client_id.encode('utf-8') + a2b_hex(seed), hashlib.sha256).hexdigest()

    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION')

        if auth is None:
            return None

        auth_match = ClientAuthentication.TOKEN_RX.match(auth)
        if auth_match is None:
            return None

        client_id = auth_match.group('cid')
        seed = auth_match.group('seed')
        token = auth_match.group('token')

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such client')

        ok_hash = self.compute_hash(client_id, seed, client.secret_bytes)

        if hmac.compare_digest(token, ok_hash):
            return ClientUser(client), None
        else:
            raise exceptions.AuthenticationFailed('Incorrect hash')
