from django import forms
from .models import Contact, PpcContact
from django.forms import TextInput

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'number', 'instahandle',)
        labels = {
            'name': '*What would you like us to call you?',
            'number': '*Your number?',
            'instahandle': 'Your Insta Handle'
        }


class PpcContactForm(forms.ModelForm):
    class Meta:
        model = PpcContact
        fields = ('name', 'email', 'contact',)
        widgets = {
            'name': TextInput(attrs={'placeholder': 'Name'}),
            'email': TextInput(attrs={'placeholder': 'Email'}),
            'contact': TextInput(attrs={'placeholder': 'Contact Number'})
        }
        labels = {
            'name': 'Name',
            'email': 'Email',
            'contact': 'Contact Number'
        }