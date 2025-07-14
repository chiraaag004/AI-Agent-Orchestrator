import pandas as pd
from langchain.tools import tool
from typing import Optional

@tool
def search_hotels(city: str, budget_range: Optional[str] = None, required_amenities: Optional[list[str]] = None) -> str:
    """
    Searches for hotels in a given city, with optional filters for budget and amenities.
    'budget_range' should be a string like '100-300'.
    'required_amenities' should be a list of strings like ['Pool', 'Spa'].
    """
    try:
        df = pd.read_csv("data/mock_hotels.csv")
        results = df[df['city'].str.lower() == city.lower()]

        if budget_range:
            min_price, max_price = map(int, budget_range.split('-'))
            results = results[(results['price_per_night'] >= min_price) & (results['price_per_night'] <= max_price)]

        if required_amenities:
            for amenity in required_amenities:
                results = results[results['amenities'].str.contains(amenity, case=False, na=False)]

        if results.empty:
            return f"No hotels found in {city} with the specified criteria."

        return results.to_string()
    except FileNotFoundError:
        return "Error: Hotel data file not found."
    except Exception as e:
        return f"An error occurred while searching for hotels: {e}"