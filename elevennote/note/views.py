from django.views.generic import CreateView, UpdateView, TemplateView
from django.utils import timezone
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import PermissionDenied

from tastypie.models import ApiKey

from .models import Note
from .mixins import LoginRequiredMixin, NoteMixin
from .forms import NoteForm


class NoteCreate(LoginRequiredMixin, NoteMixin, CreateView):
    form_class = NoteForm
    template_name = 'note/form.html'
    success_url = reverse_lazy('note:index')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.pub_date = timezone.now()
        return super(NoteCreate, self).form_valid(form)


class NoteUpdate(LoginRequiredMixin, NoteMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'note/form.html'
    success_url = reverse_lazy('note:index')

    def form_valid(self, form):
        form.instance.pub_date = timezone.now()
        return super(NoteUpdate, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.owner != self.request.user:
            raise PermissionDenied

        return super(NoteUpdate, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.owner != self.request.user:
            raise PermissionDenied

        return super(NoteUpdate, self).post(request, *args, **kwargs)


class ProfileView(NoteMixin, TemplateView):
    template_name = 'note/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        
        try:
            api_key_obj = ApiKey.objects.get(user=self.request.user)
            api_key = api_key_obj.key
        except ApiKey.DoesNotExist:
            api_key = None

        context.update({
            'api_key': api_key
        })
        return context
