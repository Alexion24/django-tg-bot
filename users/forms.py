from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms


User = get_user_model()


class CreateUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'password1', 'password2'
        )


class BroadcastForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    broadcast_text = forms.CharField(widget=forms.Textarea)