import os
import pandas as pd
from langchain.tools import tool

# Define the path to the data file relative to the project root
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_itineraries.csv')

@tool
def check_flight_itinerary(booking_reference: str) -> str:
    """
    Checks the details of a flight itinerary using a booking reference number (e.g., 'ABC123').
    Useful for checking the details of a specific flight itinerary when the user provides a booking reference.
    Do not use for general flight status; use the get_flight_status tool for that.
    """
    try:
        itineraries_df = pd.read_csv(DATA_FILE_PATH)
        # Normalize input and data for case-insensitive comparison
        itinerary = itineraries_df[itineraries_df['booking_reference'].str.lower() == booking_reference.lower()]

        if not itinerary.empty:
            details = itinerary.iloc[0]
            return (
                f"Itinerary found for booking reference {details['booking_reference']}:\n"
                f"  - Passenger: {details['passenger_name']}\n"
                f"  - Flight: {details['flight_number']} from {details['origin']} to {details['destination']}\n"
                f"  - Departure: {details['departure_time']}\n"
                f"  - Arrival: {details['arrival_time']}\n"
                f"  - Status: {details['status']}"
            )
        else:
            return f"No itinerary found for booking reference '{booking_reference}'."
    except FileNotFoundError:
        return "Error: The itinerary data file could not be found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"