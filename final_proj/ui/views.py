from django.shortcuts import render, redirect
from .models import NiftyData
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import ExtractWeekDay
from datetime import datetime, timedelta
import json
from django.contrib.auth import login, logout, authenticate
from .forms import SignupForm
from django.contrib.auth.forms import AuthenticationForm


def landing_page(request):
    # Get today's date and the date from weeks ago
    today = datetime.today()
    week_ago = today - timedelta(days=7)

    # Fetch data from the NiftyData model for the past weeks excluding weekends
    nifty_data = NiftyData.objects.annotate(
        week_day=ExtractWeekDay('date')
    ).filter(
        date__gte=week_ago,
        week_day__in=[2, 3, 4, 5, 6]  # 2=Monday, 3=Tuesday, ..., 6=Friday
    ).order_by('date')

    # Prepare data for the chart
    dates = [entry.date.strftime('%Y-%m-%d') for entry in nifty_data]
    daily_returns = [entry.daily_return for entry in nifty_data]
    cumulative_returns = [entry.cumulative_return for entry in nifty_data]
    sma_50 = [entry.sma_50 for entry in nifty_data]
    sma_200 = [entry.sma_200 for entry in nifty_data]
    adj_close = [entry.adj_close for entry in nifty_data]
    obv = [entry.obv for entry in nifty_data]

    # Get the latest standard deviation value
    if nifty_data:
        latest_std_dev = nifty_data.latest('date').standard_deviation
    else:
        latest_std_dev = 0.0

    # Get the latest market condition
    if nifty_data:
        market_condition = nifty_data.latest('date').market_condition
    else:
        market_condition = "Unknown"

    context = {
        'dates': json.dumps(dates, cls=DjangoJSONEncoder),
        'daily_returns': json.dumps(daily_returns, cls=DjangoJSONEncoder),
        'cumulative_returns': json.dumps(cumulative_returns, cls=DjangoJSONEncoder),
        'sma_50': json.dumps(sma_50, cls=DjangoJSONEncoder),
        'sma_200': json.dumps(sma_200, cls=DjangoJSONEncoder),
        'adj_close': json.dumps(adj_close, cls=DjangoJSONEncoder),
        'obv': json.dumps(obv, cls=DjangoJSONEncoder),
        'latest_std_dev': json.dumps(latest_std_dev, cls=DjangoJSONEncoder),
        'market_condition': market_condition,
        # Serialize the full data for interactivity
        'nifty_data': json.dumps(list(nifty_data.values()), cls=DjangoJSONEncoder)
    }
    return render(request, 'landing_page.html', context)


def home(request):
    return render(request, 'home.html')


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.userprofile.sectors.set(form.cleaned_data['sectors'])
            user.userprofile.stocks.set(form.cleaned_data['stocks'])
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('landing_page')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})
