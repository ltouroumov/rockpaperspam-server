# Use django.test.TestCase here so I get the snazzy Django assertions.

from django.test import TestCase
from backend.models import Room, Message

class ViewTests(TestCase):
    def test_about(self):
        r = self.client.get('/')
        self.assertTemplateUsed(r, 'backend/about.html')

    def test_new_room(self):
        r = self.client.get('/new/')
        room_label = r['Location'].strip('/')
        assert Room.objects.filter(label=room_label).exists()

    def test_chat_room(self):
        room = Room.objects.create(label='room1')
        r = self.client.get('/room1/')
        self.assertTemplateUsed(r, 'backend/room.html')
        assert r.context['room'] == room
