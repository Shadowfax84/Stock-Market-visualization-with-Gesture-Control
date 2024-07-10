from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Sector, Stock
from django_select2.forms import Select2MultipleWidget


class SignupForm(UserCreationForm):
    sectors = forms.ModelMultipleChoiceField(
        queryset=Sector.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'sector-select'}),
        required=False,
        label='Select up to 3 sectors'
    )
    stocks = forms.ModelMultipleChoiceField(
        queryset=Stock.objects.all(),
        widget=Select2MultipleWidget(attrs={'class': 'stock-select'}),
        required=False,
        label='Select up to 6 stocks'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1',
                  'password2', 'sectors', 'stocks']
