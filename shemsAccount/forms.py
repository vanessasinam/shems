from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class NewUserForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username"})
    )
    password1 = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Password"})
    )
    password2 = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Confirm Password"})
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        if commit:
            user.save()
        return user