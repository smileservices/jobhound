import requests
from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME


def check_recaptcha(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        request.recaptcha_valid = None
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            if result['success']:
                request.recaptcha_valid = True
            else:
                request.recaptcha_valid = False
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def staff_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    '''
    User has to be staff
    :param function:
    :param redirect_field_name:
    :param login_url:
    :return:
    '''

    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def super_admin_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    '''
    User has to be staff
    :param function:
    :param redirect_field_name:
    :param login_url:
    :return:
    '''

    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
