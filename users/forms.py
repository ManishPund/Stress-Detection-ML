from django import forms
from .models import UserRegistrationModel


class UserRegistrationForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'pattern': '[a-zA-Z]+', 'title': 'Enter alphabetic characters only'}),
        max_length=100
    )
    loginid = forms.CharField(
    widget=forms.TextInput(attrs={
        'pattern': '[a-zA-Z0-9]+',
        'title': 'Enter alphabetic and numeric characters only'
    }),
    max_length=100
)

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'pattern': '(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}',
            'title': 'Must contain at least one number, one uppercase and lowercase letter, and at least 8 characters'
        }),
        max_length=100
    )
    mobile = forms.CharField(
        widget=forms.TextInput(attrs={'pattern': '[56789][0-9]{9}', 'title': 'Enter a valid 10-digit mobile number'}),
        max_length=10
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'pattern': '[a-z0-9._%+\-]+@[a-z0-9.-]+\.[a-z]{2,}$', 'title': 'Enter a valid email address'}),
        max_length=100
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 22}),
        max_length=250
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'pattern': '[A-Za-z ]+', 'title': 'Enter characters only'}),
        max_length=100
    )
    state = forms.CharField(
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'pattern': '[A-Za-z ]+', 'title': 'Enter characters only'}),
        max_length=100
    )
    status = forms.CharField(
        widget=forms.HiddenInput(),
        initial='waiting',
        max_length=100
    )

    class Meta:
        model = UserRegistrationModel
        fields = '__all__'
