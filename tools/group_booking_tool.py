import pandas as pd
from langchain.tools import tool
from typing import List

@tool
def group_booking_tool(room_requests: List[dict]) -> str:
    """Handles group bookings with conflict resolution."""
    try:
        df = pd.read_csv("data/room_inventory.csv", index_col='room_type')
        bookings = []
        conflicts = []

        for request in room_requests:
            room_type = request['room_type']
            num_rooms = request['num_rooms']
            if room_type in df.index and df.loc[room_type, 'rooms_available'] >= num_rooms:
                df.loc[room_type, 'rooms_available'] -= num_rooms
                bookings.append(f"{num_rooms} {room_type} rooms booked successfully.")
            else:
                conflicts.append(f"Not enough {room_type} rooms available.")

        df.to_csv("data/room_inventory.csv")

        response = ""
        if bookings:
            response += "\n".join(bookings)
        if conflicts:
            response += "\n".join(conflicts)

        return response

    except FileNotFoundError:
        return "Room inventory data not found."