from django import forms
from .models import NewsletterSubscription

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['name','email']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-control'})
        }
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox,ReCaptchaV3

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Your Name"
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Your Email"
    }))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Subject"
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control",
        "rows": 6,
        "placeholder": "Message"
    }))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
