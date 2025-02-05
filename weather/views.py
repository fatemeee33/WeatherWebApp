from django.shortcuts import render, redirect
import requests
from .models import City
from .forms import CityForm
import logging

logger = logging.getLogger(__name__)

# OpenWeatherMap API Base URL
API_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=5e80937bbd016176bbedd5253600ae18&units=metric'


def index(request):
    err_msg = ''
    message = ''
    message_class = ''

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.cleaned_data['name']
            existing_city_count = City.objects.filter(name=new_city).count()

            if existing_city_count == 0:
                response = requests.get(API_URL.format(new_city)).json()
                if response.get('cod') == 200:  # Ensure cod is checked correctly
                    form.save()
                    message = 'City added successfully!'
                    message_class = 'is-success'
                else:
                    err_msg = 'City does not exist!'
            else:
                err_msg = 'City already exists!'

        if err_msg:
            message = err_msg
            message_class = 'is-danger'

    form = CityForm()
    cities = City.objects.all()
    weather_data = []

    for city in cities:
        response = requests.get(API_URL.format(city.name)).json()

        if response.get('cod') == 200:
            city_weather = {
                'city': city.name,
                'temperature': response['main']['temp'],
                'description': response['weather'][0]['description'],
                'icon': response['weather'][0]['icon'],
            }
            weather_data.append(city_weather)
        else:
            logger.warning(f"Could not retrieve weather data for {city.name}: {response}")

    context = {
        'weather_data': weather_data,
        'form': form,
        'message': message,
        'message_class': message_class
    }
    return render(request, 'weather/weather.html', context)


def delete_city(request, city_name):
    City.objects.filter(name=city_name).delete()
    return redirect('home')
