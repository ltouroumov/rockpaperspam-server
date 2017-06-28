from django import forms
from api.models import Notification, Client
import json


class CreateClientForm(forms.Form):
    display_name = forms.CharField()
    phone_number = forms.CharField(initial='+0')

    is_staff = forms.BooleanField(initial=False, required=False)
    is_bot = forms.BooleanField(initial=False, required=False)


class ClientChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} ({})".format(obj.profile.display_name, obj.id)


class JsonField(forms.CharField):

    def to_python(self, value):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON data")


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['client', 'template', 'title_args', 'body_args']

    client = ClientChoiceField(queryset=Client.objects.order_by('profile__display_name'))
    title_args = JsonField(initial=[], required=False)
    body_args = JsonField(initial=[], required=False)
