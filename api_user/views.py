from django.shortcuts import render

# Create your views here.
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.views import PasswordChangeView
from api_user.mixins import LoginRequiredMixin


import logging

from api_user.models import ApiUser
from api_user.forms import ApiUserSignupForm, ApiUserUpdateForm
from api_user.decorators import check_recaptcha

main_logger = logging.getLogger('main')


class RegisterView(CreateView):
    # model = Supplier
    form_class = ApiUserSignupForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    @method_decorator(check_recaptcha)
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid() and request.recaptcha_valid:
            main_logger.info('api user registered account..')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


def api_user_dashboard(request):
    return render(request, 'dashboard/main.html')


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    model = ApiUser
    template_name = 'dashboard/account.html'
    form_class = ApiUserUpdateForm
    login_url = 'api_user-login'
    
    def get_object(self, queryset=None):
        return self.model.objects.get(user_ptr_id=self.request.user.id)

    # def get(self, request, *args, **kwargs):
    #     self.object = request.user
    #     return self.render_to_response(self.get_context_data())
    # 
    # def post(self, request, *args, **kwargs):
    #     self.object = self.model.objects.get(user_ptr_id=request.user.id)
    #     form = self.get_form()
    #     if form.is_valid():
    #         return self.form_valid(form)
    #     else:
    #         return self.form_invalid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProfileUpdate, self).get_context_data(object_list=None, **kwargs)
        context['page'] = {
            'title': 'Update Profile',
            'bc1': 'Profile',
            'bc2': 'Update',
        }
        return context
    
class UpdatePassword(LoginRequiredMixin, PasswordChangeView):
    model = ApiUser
    template_name = 'dashboard/form.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UpdatePassword, self).get_context_data(object_list=None, **kwargs)
        context['page'] = {
            'title': 'Change Password',
            'bc1': 'Account',
            'bc2': 'Password',
        }
        return context
