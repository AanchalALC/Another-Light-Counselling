from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'number', 'instahandle',)
        labels = {
            'name': '*What would you like us to call you?',
            'number': '*Your number?',
            'instahandle': 'Your Insta Handle'
        }