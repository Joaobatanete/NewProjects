import os
import requests
import urllib.parse
import datetime

from flask import Flask, redirect, render_template, request, session
from functools import wraps

# Get actual date-time.
def today_date():
    
    tday = datetime.date.today()
    
    return tday

# Fuction to prevent acess to other route if login not executed.
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function

# Check the Real-Time Weather Data from the City from the API. 
def lookup(city):
    
    api_key = os.environ.get("API_KEY")
    
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}'
    
    response = requests.get(url.format(city)).json()
    
    # if it doesn´t exists create an non-existent dictionary.
    if response['cod'] == '404':
        
        weather = {
            
            "code" : response['cod'],
            "city" : "Not Found"
            
        }
    
    # if it does then create the correct data dictionary.
    else:
        weather = {
        
            "city" : response['city']['name'],
            "country": response['city']['country'],
            "temperature" : round((float(response['list'][0]['main']['temp']) - 272.15)),
            "description" : response['list'][1]['weather'][0]['description'],
            "humidity" : response['list'][0]['main']['humidity'],
            "wind" :response['list'][1]['wind']['speed'],
            "icon" : response['list'][1]['weather'][0]['icon']
        
        }
    
    return weather