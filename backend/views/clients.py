import json

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View, DetailView, ListView, DeleteView, FormView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin

from api.firebase import FirebaseCloudMessaging
from api.models import Client, Contact
from backend import settings
from backend.models import Endpoint
from backend.utils import ModelChoiceFieldWithLabel
from backend.forms import CreateClientForm


class Index(LoginRequiredMixin, ListView):
    model = Client
    template_name = "backend/clients/index.html"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().order_by('creation_date', 'id')
        if "q" in self.request.GET:
            q = self.request.GET['q']
            if len(q) > 0:
                qs = qs.filter(profile__display_name__icontains=q)

        return qs


class Show(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "backend/clients/show.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            tab_name=self.request.GET.get('tab', 'contacts')
        )


class Create(LoginRequiredMixin, FormView):
    form_class = CreateClientForm
    template_name = "backend/clients/form.html"
    success_url = reverse_lazy('clients')

    def form_valid(self, form):
        import uuid

        client = Client(id=uuid.uuid4())
        client.is_staff = form.cleaned_data['is_staff']
        client.is_bot = form.cleaned_data['is_bot']

        profile = Contact.objects.create(contact_id=0, contact_key='profile',
                                         display_name=form.cleaned_data['display_name'])
        profile_raw = profile.raw_contacts.create(contact_type='com.android.profile',
                                                  contact_name='Profile')
        profile_raw.data.create(type='NAME', value=form.cleaned_data['display_name'])
        profile_raw.data.create(type='PHONE', value=form.cleaned_data['phone_number'])
        client.profile = profile

        client.save()

        return super().form_valid(form)


class Delete(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "backend/clients/delete.html"
    success_url = reverse_lazy('clients')


class DeleteMulti(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = "backend/clients/delete_multi.html"

    def get(self, request, *args, **kwargs):
        return redirect('clients')

    def post(self, request, *args, **kwargs):
        clients = [Client.objects.get(id=cid) for cid in request.POST.getlist('ids[]')]

        confirm = request.POST.get('confirm', 'false')
        if confirm == 'true':
            for client in clients:
                client.delete()

            messages.info(request, "Clients deleted")
            return redirect('clients')
        else:
            return self.render_to_response({
                'clients': clients
            })


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

        action = request.GET.get('action', None)
        data = {}
        if action == 'sync':
            data['action'] = 'sync'

        context = self.get_context_data(form=SendForm(data={'data': json.dumps(data)}))
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

        return redirect(to='show_client', pk=object.id)


class CloneForm(forms.Form):
    endpoint = ModelChoiceFieldWithLabel(
        label="Endpoint",
        custom_label=lambda obj: str.format("{0} ({1})", obj.name, obj.number),
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
            target = form.cleaned_data['endpoint']

            firebase = FirebaseCloudMessaging(server_key=settings.GCM_SERVER_KEY)
            firebase.send(to=client.token, payload={
                'action': 'dupe',
                'contact_id': contact.contact_id,
                'contact_key': contact.contact_key,
                'target': target.number
            })

            messages.success(request, "Contact Cloned")
            return redirect(to='show_client', pk=pk)
        else:
            return self.render_to_response({
                'client': client,
                'contact': contact,
                'form': form
            })
