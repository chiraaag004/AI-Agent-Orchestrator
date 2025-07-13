from langchain.tools import tool
from pydantic import BaseModel, Field

class FlightStatusInput(BaseModel):
    """Input for the flight status tool."""
    flight_number: str = Field(description="The flight number to check, for example, 'UA123' or 'BA456'.")

def _get_flight_status(flight_number: str) -> str:
    """A placeholder function to simulate checking a flight's status."""
    print(f"--- Checking status for flight: {flight_number} ---")
    # In a real application, you would call an API here.
    # For this example, we'll just return a static status.
    return f"🛫 Flight {flight_number} is currently ON TIME."

@tool(args_schema=FlightStatusInput)
def flight_status_tool(flight_number: str) -> str:
    """
    Use this tool to check the real-time status of a specific flight.
    You must provide the flight number.
    """
    return _get_flight_status(flight_number)
