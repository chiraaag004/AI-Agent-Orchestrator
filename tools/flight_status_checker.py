import os
import pandas as pd
from langchain.tools import tool

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_flight_status.csv')

@tool
def get_flight_status(flight_number: str) -> str:
    """
    Checks the real-time status of a flight using its flight number (e.g., 'UA456').
    Useful for checking the current status of a specific flight.
    Do not use for checking itineraries with booking references; use the check_flight_itinerary tool for that.
    """
    try:
        status_df = pd.read_csv(DATA_FILE_PATH)
        # Normalize for case-insensitive comparison
        status = status_df[status_df['flight_number'].str.lower() == flight_number.lower()]

        if not status.empty:
            details = status.iloc[0]
            return (
                f"Status for flight {details['flight_number']}:\n"
                f"  - Status: {details['status']}\n"
                f"  - Gate: {details['gate']}\n"
                f"  - Scheduled Departure: {details['scheduled_departure']}\n"
                f"  - Estimated Departure: {details['estimated_departure']}"
            )
        else:
            return f"No status information found for flight number '{flight_number}'."
    except FileNotFoundError:
        return "Error: The flight status data file could not be found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"