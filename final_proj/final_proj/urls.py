"""
URL configuration for final_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ui.views import *

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('admin/', admin.site.urls),
    path('home/', home, name='home'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('get_stocks/', get_stocks, name='get_stocks'),
    path('get_visualizations/', get_visualizations, name='get_visualizations'),
    path('portfolio_analysis/', portfolio_analysis, name='portfolio_analysis'),
    path('general_analysis/', general_analysis, name='general_analysis'),
]
