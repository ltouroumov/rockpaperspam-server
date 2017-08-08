import json

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import View, DetailView, ListView, DeleteView, UpdateView, FormView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin

from api.firebase import FirebaseCloudMessaging
from api.models import Client, Contact, Energy, Notification, RawContact, Data
from api.serializers import RawContactSerializer
from backend.forms import CreateClientForm
from backend.models import Endpoint
from backend.utils import ModelChoiceFieldWithLabel
from rps_cnc import settings


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


class EditEnergy(LoginRequiredMixin, UpdateView):
    model = Energy
    fields = ['pool_size', 'regen_rate']
    template_name = "backend/clients/form_energy.html"

    def get_object(self, queryset=None):
        if not queryset:
            queryset = super().get_queryset()

        pk = self.kwargs.get('pk')
        queryset = queryset.filter(client__id=pk)

        obj = queryset.get()
        return obj

    def get_success_url(self):
        return reverse('show_client', args=(self.object.client.id,)) + "?tab=energy"


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


class Reset(LoginRequiredMixin, SingleObjectMixin, TemplateResponseMixin, View):
    model = Client
    template_name = "backend/alert.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'alert_type': 'danger',
            'alert_title': 'Reset client data?',
            'alert_body': 'Do you want to erase all data for this client?',
            'alert_cancel': reverse('clients')
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        ctx = self.get_context_data()
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        try:
            obj.token = ''
            obj.profile.reset()
            obj.contacts.all().delete()
            obj.games.delete()
            obj.sync_set.all().delete()
            obj.energy.reset()
            obj.save()
        except:
            from traceback import print_exc
            print_exc()
            messages.error(request, 'Failed to reset client!')

        messages.info(request, 'Client reset')
        return redirect('clients')


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

            firebase.send(to=object.token, payload=args)
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


class ContactClone(LoginRequiredMixin, FormView):
    template_name = "backend/clients/contacts/form.html"
    form_class = CloneForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_title'] = "Create Contact"
        ctx['client'] = Client.objects.get(id=self.kwargs['pk'])

        return ctx

    def get_success_url(self):
        return reverse('show_client', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):

        client = Client.objects.get(id=self.kwargs['pk'])
        contact = client.contacts.get(id=self.kwargs['cid'])

        target = form.cleaned_data['endpoint']

        Notification(client=client, data={
            'action': 'contact.dup',
            'contact_id': contact.contact_id,
            'contact_key': contact.contact_key,
            'target': target.number
        }).save()

        messages.success(self.request, "Contact Cloned")

        return super().form_valid(form)


class ContactForm(forms.Form):
    display_name = forms.CharField()
    phone_number = forms.CharField()


class ContactCreate(LoginRequiredMixin, FormView):
    template_name = "backend/clients/contacts/form.html"
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_title'] = "Create Contact"
        ctx['client'] = Client.objects.get(id=self.kwargs['pk'])

        return ctx

    def get_success_url(self):
        return reverse('show_client', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):

        client = Client.objects.get(id=self.kwargs['pk'])

        payload = {
            'id': 0,
            'contact_type': 'mitc',
            'contact_name': 'MitC',
            'data': [
                {'type': 'NAME', 'value': form.cleaned_data['display_name']},
                {'type': 'PHONE', 'value': form.cleaned_data['phone_number']},
            ]
        }

        print("payload:" + repr(payload))

        Notification(client=client, data={
            'action': 'contact.new',
            'payload': json.dumps(payload)
        }).save()

        messages.success(self.request, "Create request sent")

        return super(ContactCreate, self).form_valid(form)


class LinkForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all())


class ContactLink(LoginRequiredMixin, FormView):
    template_name = "backend/clients/contacts/link.html"
    form_class = LinkForm

    def get_success_url(self):
        return reverse('show_client', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_title'] = "Link Contact"
        ctx['client'] = Client.objects.get(id=self.kwargs['pk'])

        return ctx

    def form_valid(self, form):

        client = Client.objects.get(id=self.kwargs['pk'])

        target = form.cleaned_data['client']
        payload = RawContactSerializer(target.profile.raw_contacts.first()).data

        print("payload:" + repr(payload))

        Notification(client=client, data={
            'action': 'contact.new',
            'payload': payload
        }).save()

        messages.success(self.request, "Link request sent")

        return super().form_valid(form)


class ContactDelete(LoginRequiredMixin, SingleObjectMixin, TemplateResponseMixin, View):
    model = Contact
    pk_url_kwarg = 'cid'
    template_name = "backend/alert.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'alert_type': 'danger',
            'alert_title': 'Delete contact {}?'.format(self.object.display_name),
            'alert_body': 'This will permanently erase the contact from the device!',
            'alert_cancel': reverse('show_client', args=(self.kwargs['pk'],))
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        ctx = self.get_context_data(**kwargs)
        return self.render_to_response(ctx)

    def post(self, request, pk, *args, **kwargs):

        contact = self.get_object()
        client = Client.objects.get(id=pk)

        Notification(client=client, data={
            'action': 'contact.del',
            'contact_id': contact.contact_id,
            'contact_key': contact.contact_key
        }).save()

        messages.success(request, "Deletion request sent")

        return redirect(to='show_client', pk=pk)
