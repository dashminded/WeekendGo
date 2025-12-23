from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *

from .models import Booking



class pgform(forms.ModelForm):
    class Meta:
        model=pg
        fields='__all__'


class ownerform(forms.ModelForm):
    class Meta:
        model=owner
        fields='__all__'

class feedbackdorm(forms.ModelForm):
    class Meta:
        model=feedback
        fields='__all__'


class RegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields = '__all__'




class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }