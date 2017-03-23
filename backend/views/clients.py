from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import View, DetailView, ListView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django import forms
from django.contrib import messages
from api.models import Client
from backend import settings
from backend.firebase import FirebaseCloudMessaging
import json

from backend.models import Endpoint


class Index(LoginRequiredMixin, ListView):
    model = Client
    template_name = "backend/clients/index.html"


class Show(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "backend/clients/show.html"


class SendForm(forms.Form):
    notif_title = forms.CharField(
        label="Notification Title",
        required=False)

    notif_body = forms.CharField(
        label="Notification Body",
        required=False)

    data = forms.CharField(
        label="Data Payload",
        initial="{}",
        widget=forms.Textarea)


class Send(LoginRequiredMixin, SingleObjectMixin, TemplateResponseMixin, View):
    model = Client
    template_name = "backend/clients/send.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(form=SendForm())
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        object = self.get_object()

        form = SendForm(request.POST)

        if form.is_valid():
            firebase = FirebaseCloudMessaging(server_key=settings.GCM_SERVER_KEY)

            args = {
                'data': json.loads(form.cleaned_data['data'])
            }

            if form.cleaned_data['notif_title'] or form.cleaned_data['notif_body']:
                args['notification'] = {
                    'title': form.cleaned_data['notif_title'],
                    'body': form.cleaned_data['notif_body']
                }

            firebase.send(to=object.token, **args)
            messages.info(request, "Notification Sent")
        else:
            messages.error(request, "Form is not valid")

        return redirect(to='send_client', pk=object.id)


class CloneForm(forms.Form):
    endpoint = forms.ModelChoiceField(
        label="Endpoint",
        required=True,
        queryset=Endpoint.objects.all())


class Clone(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = "backend/clients/clone.html"

    def get(self, request, pk, cid, *args, **kwargs):
        client = Client.objects.get(id=pk)
        contact = client.friends.get(id=cid)

        return self.render_to_response({
            'client': client,
            'contact': contact,
            'form': CloneForm()
        })

    def post(self, request, pk, cid, *args, **kwargs):
        client = Client.objects.get(id=pk)
        contact = client.friends.get(id=cid)

        form = CloneForm(request.POST)
        if form.is_valid():
            messages.success(request, "Contact Cloned")

            # TODO: Send clone notification

            return redirect(to='show_client', pk=pk)
        else:
            return self.render_to_response({
                'client': client,
                'contact': contact,
                'form': form
            })
