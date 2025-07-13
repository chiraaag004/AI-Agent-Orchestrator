from langchain.tools import tool

@tool
def book_flight_tool(query: str) -> str:
    """Book a flight for the user. Must include destination in the query."""
    # Simulate destination detection
    for city in ["Delhi", "Mumbai", "Bangalore", "Chennai"]:
        if city.lower() in query.lower():
            return f"✈️ Flight to {city} booked successfully for tomorrow!"
    return "Please mention a valid destination like Delhi, Mumbai, Bangalore, or Chennai."
