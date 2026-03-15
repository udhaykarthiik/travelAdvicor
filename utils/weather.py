import requests
import os

def get_weather(city, api_key):
    """Get current weather for a city"""
    try:
        # Map common destinations
        city_map = {
            'manali': 'Manali,IN',
            'kerala': 'Kochi,IN',
            'delhi': 'Delhi,IN',
            'goa': 'Panaji,IN',
            'mumbai': 'Mumbai,IN',
            'jaipur': 'Jaipur,IN',
            'agra': 'Agra,IN'
        }
        
        api_city = city_map.get(city.lower(), f"{city},IN")
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={api_city}&appid={api_key}&units=metric"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'].title(),
                'city': data['name'],
                'country': data['sys']['country']
            }
    except:
        return None

def get_weather_icon(description):
    """Get weather icon class"""
    desc = description.lower() if description else ''
    
    if 'clear' in desc:
        return 'bi-brightness-high-fill text-warning'
    elif 'cloud' in desc:
        return 'bi-cloud-fill text-secondary'
    elif 'rain' in desc:
        return 'bi-cloud-rain-fill text-primary'
    elif 'thunder' in desc:
        return 'bi-cloud-lightning-rain-fill text-danger'
    elif 'snow' in desc:
        return 'bi-snow text-info'
    else:
        return 'bi-cloud-sun-fill text-warning'