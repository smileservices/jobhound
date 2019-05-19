"""jobhound URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
from django.urls import path, reverse_lazy

from django.contrib.auth import views as auth_views
import api_user.views as api_user_views

# Registration & Login
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name="api_user-login"),
    path('logout/', auth_views.LogoutView.as_view(), name="api_user-logout"),
    # password reset
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        html_email_template_name='registration/password_reset_email.html'
    ), name="password_reset"),
    path('accounts/password_reset/confirm/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_email_sent.html'
    ), name="password_reset_done"),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name="password_reset_link"),
    path('accounts/password_reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name="password_reset_complete"),
    # registration
    path('register/', api_user_views.RegisterView.as_view(), name="register"),
    # social auth
    # path('auth/', include('social_django.urls', namespace='social')),
]

# API User Dashboard
urlpatterns += [
    path('profile', api_user_views.ProfileUpdate.as_view(success_url=reverse_lazy('api_user-profile')),
         name='api_user-profile'),
    path('settings/api_user/password', api_user_views.UpdatePassword.as_view(success_url=reverse_lazy('api_user-profile')),
         name='api_user-password')
]
