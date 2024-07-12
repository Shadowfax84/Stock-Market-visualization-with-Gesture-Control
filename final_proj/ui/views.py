from django.shortcuts import render, redirect
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import ExtractWeekDay
from datetime import datetime, timedelta
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import NiftyData, StockData, Sector, Stock
from .forms import SignupForm
import json


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
            return redirect('login')
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
                return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required
def dashboard_view(request):
    user_profile = request.user.userprofile
    sectors = user_profile.sectors.all()
    return render(request, 'dashboard.html', {'sectors': sectors})


@login_required
def get_stocks(request):
    sector_id = request.GET.get('sector_id')
    user_profile = request.user.userprofile
    if sector_id == 'all':
        stocks = user_profile.stocks.all()
    else:
        stocks = user_profile.stocks.filter(sector__id=sector_id)
    stock_list = [{'id': stock.id, 'name': stock.name} for stock in stocks]
    return JsonResponse({'stocks': stock_list})


@login_required
def get_visualizations(request):
    today = datetime.now().date()
    one_month_ago = today - timedelta(days=30)

    stock_id = request.GET.get('stock_id')
    if stock_id == 'all':
        stock_data = StockData.objects.filter(
            stock__userprofile=request.user.userprofile,
            date__gte=one_month_ago
        )
        stock_name = "All Stocks"
    else:
        stock_data = StockData.objects.filter(
            stock__id=stock_id,
            date__gte=one_month_ago
        )

    dates = [data.date for data in stock_data]
    open_prices = [data.open for data in stock_data]
    high_prices = [data.high for data in stock_data]
    low_prices = [data.low for data in stock_data]
    close_prices = [data.close for data in stock_data]
    daily_returns = [data.daily_return for data in stock_data]
    cumulative_returns = [data.cumulative_return for data in stock_data]
    obv = [data.obv for data in stock_data]
    force_index = [data.force_index for data in stock_data]

    # Key metrics for summary cards
    if stock_data.exists():
        latest_close = close_prices[-1]
        previous_close = close_prices[-2] if len(
            close_prices) > 1 else latest_close
        price_change = latest_close - previous_close
        price_change_percent = (
            price_change / previous_close) * 100 if previous_close else 0
        latest_obv = obv[-1]
        latest_force_index = force_index[-1]
        volatility = stock_data.latest('date').standard_deviation
    else:
        latest_close = previous_close = price_change = price_change_percent = 0
        latest_obv = latest_force_index = volatility = 0

    # Prepare data for Candlestick chart
    candlestick_data = {
        'x': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices
    }

    # Prepare data for Returns chart
    returns_data = {
        'dates': dates,
        'daily_returns': daily_returns,
        'cumulative_returns': cumulative_returns
    }

    # Prepare data for OBV and Force Index chart
    obv_data = {
        'dates': dates,
        'obv': obv,
        'force_index': force_index
    }

    return JsonResponse({
        'candlestick': candlestick_data,
        'returns': returns_data,
        'obv': obv_data,
        'summary': {
            'latest_close': latest_close,
            'price_change': price_change,
            'price_change_percent': price_change_percent,
            'latest_obv': latest_obv,
            'latest_force_index': latest_force_index,
            'volatility': volatility
        }
    })


@login_required
def portfolio_analysis(request):
    return render(request, 'portfolio_analysis.html')


@login_required
def general_analysis(request):
    return render(request, 'general_analysis.html')


@login_required
def get_sectors(request):
    sectors = Sector.objects.all().values('id', 'name')
    return JsonResponse(list(sectors), safe=False)


@login_required
def get_stocks_by_sector(request):
    sector_id = request.GET.get('sector_id')
    if sector_id == 'all':
        stocks = Stock.objects.all().values('id', 'name')
    else:
        stocks = Stock.objects.filter(
            sector__id=sector_id).values('id', 'name')
    return JsonResponse({'stocks': list(stocks)}, safe=False)


@login_required
def get_genvisuals(request):
    today = datetime.now().date()
    one_month_ago = today - timedelta(days=30)

    stock_id = request.GET.get('stock')
    if stock_id == 'all':
        stock_data = StockData.objects.filter(date__gte=one_month_ago)
    else:
        stock_data = StockData.objects.filter(
            stock__id=stock_id, date__gte=one_month_ago)

    dates = [data.date for data in stock_data]
    open_prices = [data.open for data in stock_data]
    high_prices = [data.high for data in stock_data]
    low_prices = [data.low for data in stock_data]
    close_prices = [data.close for data in stock_data]
    daily_returns = [data.daily_return for data in stock_data]
    cumulative_returns = [data.cumulative_return for data in stock_data]
    sma_50 = [data.sma_50 for data in stock_data]
    sma_200 = [data.sma_200 for data in stock_data]
    obv = [data.obv for data in stock_data]
    force_index = [data.force_index for data in stock_data]

    # Key metrics for summary cards
    if stock_data.exists():
        latest_close = close_prices[-1]
        previous_close = close_prices[-2] if len(
            close_prices) > 1 else latest_close
        price_change = latest_close - previous_close
        price_change_percent = (
            price_change / previous_close) * 100 if previous_close else 0
        latest_obv = obv[-1]
        latest_force_index = force_index[-1]
        volatility = stock_data.latest('date').standard_deviation
    else:
        latest_close = previous_close = price_change = price_change_percent = 0
        latest_obv = latest_force_index = volatility = 0

    # Prepare data for Candlestick chart
    candlestick_data = {
        'x': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices
    }

    # Prepare data for Returns chart
    returns_data = {
        'dates': dates,
        'daily_returns': daily_returns,
        'cumulative_returns': cumulative_returns
    }

    # Prepare data for OBV and Force Index chart
    obv_data = {
        'dates': dates,
        'obv': obv,
        'force_index': force_index
    }

    return JsonResponse({
        'candlestick': candlestick_data,
        'price_chart': {
            'dates': dates,
            'close_prices': close_prices,
            'sma_50': sma_50,
            'sma_200': sma_200
        },
        'returns': returns_data,
        'obv': obv_data,
        'summary': {
            'latest_close': latest_close,
            'price_change': price_change,
            'price_change_percent': price_change_percent,
            'latest_obv': latest_obv,
            'latest_force_index': latest_force_index,
            'volatility': volatility
        }
    })
