import requests


class FirebaseCloudMessaging:
    def __init__(self, server_key):
        self.server_key = server_key

    def send(self, to, **kwargs):
        resp = requests.post(
            url="https://fcm.googleapis.com/fcm/send",
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'key=%s' % self.server_key
            },
            json={
                'to': to,
                **kwargs
            })

        print(resp.content.decode('utf-8'))
