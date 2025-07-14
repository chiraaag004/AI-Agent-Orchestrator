import pandas as pd
from langchain.tools import tool
from datetime import datetime

@tool
def get_weather_forecast(city: str, date: str) -> str:
    """
    Gets the weather forecast for a specific city and date.
    Date should be in YYYY-MM-DD format.
    """
    try:
        df = pd.read_csv("data/mock_weather.csv")
        # Ensure date formats match for comparison
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        result = df[(df['city'].str.lower() == city.lower()) & (df['date'] == date)]

        if result.empty:
            return f"No weather forecast found for {city} on {date}."

        return result.to_string()
    except FileNotFoundError:
        return "Error: Weather data file not found."
    except Exception as e:
        return f"An error occurred while fetching the weather: {e}"