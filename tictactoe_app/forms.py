from django import forms
from .models import TicTacToeUser

class UserForm(forms.ModelForm):
    class Meta:
        model = TicTacToeUser
        fields = ['username', 'password', 'email', 'account_type']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 5 or len(username) > 15:
            raise forms.ValidationError("Username must be between 7 and 15 characters long.")
        return username

    def clean_account_type(self):
        account_type = self.cleaned_data.get('account_type')
        if account_type not in [1, 2]:
            raise forms.ValidationError("Account type must be 1 or 2.")
        return account_type