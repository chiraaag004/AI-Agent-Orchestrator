import pandas as pd
from langchain.tools import tool

@tool
def check_availability_tool(room_type: str) -> str:
    """Checks the availability of a given room type and provides dynamic pricing."""
    try:
        df = pd.read_csv("data/room_inventory.csv")
        room_info = df[df["room_type"] == room_type].iloc[0]
        availability_percentage = room_info["rooms_available"] / room_info["total_rooms"]
        
        if availability_percentage > 0.5:
            price_multiplier = 1.0
        elif availability_percentage > 0.2:
            price_multiplier = 1.2
        else:
            price_multiplier = 1.5
            
        dynamic_price = room_info["base_price"] * price_multiplier
        
        return f"There are {room_info['rooms_available']} {room_type} rooms available. The current price is ${dynamic_price:.2f} per night."
    except (FileNotFoundError, IndexError):
        return f"Information for {room_type} rooms is not available."