from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Field
from api_user.models import ApiUser


class ApiUserSignupForm(UserCreationForm):
    class Meta:
        model = ApiUser
        fields = ('username', 'email')


class ApiUserUpdateForm(UserChangeForm):
    class Meta:
        model = ApiUser
        fields = ('username', 'email', 'api_key')

        def __init__(self):
            self.helper = FormHelper()
            self.helper.layout = Layout(
                'username',
                'email',
                Field('api_key', readonly=True)
            )
