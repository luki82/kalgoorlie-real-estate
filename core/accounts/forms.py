#account/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# Get the User model (usually the default Django user)
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. We will use this to log you in.")
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        # We only show these fields. 'username' is hidden and set automatically below.
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Add Bootstrap styling ('form-control') to ALL fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        # 2. Clear the Email field attributes
        self.fields['email'].widget.attrs.update({
            'autocomplete': 'off',
            'placeholder': 'name@example.com',
        })
        
        # 3. Stop browsers from auto-filling the password fields
        for field in self.fields:
            if 'password' in field:
                self.fields[field].widget.attrs.update({
                    'autocomplete': 'new-password', # Tells browser "This is a new account"
                    'placeholder': '',
                })

    def clean_email(self):
        """
        Ensure the email is unique, as we are using it as the username.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        """
        Save the user, forcing the Username to be the same as the Email.
        """
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]  # <--- The Magic Trick
        
        if commit:
            user.save()
        return user