from django import forms
from .models import Contact, PpcContact
from django.forms import TextInput
from django.core.validators import RegexValidator

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'number', 'instahandle',)
        phone_regex = RegexValidator(
        regex=r'^[\d\s\+\-\(\)]+$', 
        message="Phone number must be valid. Only digits, spaces, and symbols like +, -, () are allowed."
        )
    
        # Apply it to the field
        number = forms.CharField(
            validators=[phone_regex], 
            max_length=20, 
            required=True
        )
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