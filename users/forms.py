from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import User


class CreateUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class BroadcastForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    broadcast_text = forms.CharField(widget=forms.Textarea)