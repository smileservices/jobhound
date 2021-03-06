from django.shortcuts import redirect
from django.views.generic import UpdateView
from django.template import loader
from api_key.models import APIKey
from api_key.forms import ApiKeyForm


# Create your views here.

class ApiKeyUpdate(UpdateView):
    model = APIKey
    template_name = 'dashboard/key.html'
    form_class = ApiKeyForm
    login_url = 'api_user-login'

    def get_object(self, queryset=None):
        return self.model.objects.get(user_id=self.request.user.id)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ApiKeyUpdate, self).get_context_data(object_list=None, **kwargs)
        context['page'] = {
            'title': 'Update Key',
            'bc1': 'Profile',
            'bc2': 'API Key',
        }
        return context

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        object.api_key = object.generate_key()
        object.save()
        return redirect(self.success_url)
