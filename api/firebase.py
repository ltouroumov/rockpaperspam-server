import requests


class FirebaseCloudMessaging:
    def __init__(self, server_key):
        self.server_key = server_key

    def send(self, to, payload, multicast=False):

        json = {}

        if multicast:
            json['registration_ids'] = to
        else:
            json['to'] = to

        json.update(payload)

        resp = requests.post(
            url="https://fcm.googleapis.com/fcm/send",
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'key=%s' % self.server_key
            },
            json=json)

        print(resp.content.decode('utf-8'))

    def send_data(self, to, data):
        self.send(to, payload={'data': data})

    def send_notification(self, to, notification, data=None):
        self.send(to, payload={'notification': notification, 'data': data})
