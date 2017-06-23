from django import forms


class CreateClientForm(forms.Form):
    display_name = forms.CharField()
    phone_number = forms.CharField(initial='+0')

    is_staff = forms.BooleanField(initial=False, required=False)
    is_bot = forms.BooleanField(initial=False, required=False)

