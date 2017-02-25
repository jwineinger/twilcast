from django import forms

class BroadcastForm(forms.Form):
    from django.contrib.localflavor.us.forms import USPhoneNumberField
    phone_number = USPhoneNumberField()
