import os
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import List
import random
import pandas as pd
import csv

# ----------------- Input Schemas -----------------

class BookRoomInput(BaseModel):
    guest_name: str = Field(description="Name of the guest making the reservation.")
    room_type: str = Field(description="Type of room requested (e.g., 'single', 'double', 'suite').")
    check_in_date: str = Field(description="Check-in date (YYYY-MM-DD).")
    check_out_date: str = Field(description="Check-out date (YYYY-MM-DD).")

class RoomServiceInput(BaseModel):
    guest_name: str = Field(description="Name of the guest requesting service.")
    items: List[str] = Field(description="List of items requested (e.g., ['water', 'towels', 'pizza']).")
    delivery_time: str = Field(description="Requested delivery time (HH:MM).")

class FAQInput(BaseModel):
    keyword: str = Field(description="Keyword to search for in the hotel FAQs.")

class GetHotelInfoInput(BaseModel):
    information_type: str = Field(description="Type of information requested (e.g., 'pool hours', 'gym location', 'breakfast times').")

class GetRoomDetailsInput(BaseModel):
    guest_name: str = Field(description="Name of the guest.")
    room_number: int = Field(description="Room number of the guest.")

# ----------------- Setup -----------------

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def safe_append_csv(data: dict, file_path: str, fieldnames: List[str]):
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

# ----------------- Tools -----------------

@tool(args_schema=BookRoomInput)
def book_room_tool(guest_name: str, room_type: str, check_in_date: str, check_out_date: str) -> str:
    """Simulates booking a hotel room. Logs the booking to bookings.csv."""
    confirmation_number = "HCN-" + "".join([str(x) for x in random.sample(range(10), 6)])
    data = {
        "confirmation_number": confirmation_number,
        "guest_name": guest_name,
        "room_type": room_type,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date
    }
    bookings_file = os.path.join(DATA_DIR, "bookings.csv")
    safe_append_csv(data, bookings_file, list(data.keys()))

    return f"✅ Room booked for {guest_name}: {room_type} from {check_in_date} to {check_out_date}.\nConfirmation number: {confirmation_number}"

@tool(args_schema=RoomServiceInput)
def room_service_tool(guest_name: str, items: List[str], delivery_time: str) -> str:
    """Simulates requesting room service and logs it to room_service.csv."""
    items_str = ", ".join(items)
    data = {
        "guest_name": guest_name,
        "items": items_str,
        "delivery_time": delivery_time,
        "status": "In Progress"
    }
    service_file = os.path.join(DATA_DIR, "room_service.csv")
    safe_append_csv(data, service_file, list(data.keys()))

    return f"🛎️ Room service requested by {guest_name}:\n- Items: {items_str}\n- Delivery at: {delivery_time}\nYour order will arrive shortly."

@tool(args_schema=FAQInput)
def hotel_faq_tool(keyword: str) -> str:
    """Returns hotel FAQs based on a keyword. Reads from faqs.csv."""
    faq_file = os.path.join(DATA_DIR, "faqs.csv")
    if not os.path.exists(faq_file):
        return "FAQ data file not found."

    df = pd.read_csv(faq_file)
    result = df[df["keyword"].str.contains(keyword.lower(), na=False)]
    if not result.empty:
        return result.iloc[0]["answer"]
    return "❌ Could not find an FAQ matching your keyword. Please try a related term."

@tool(args_schema=GetHotelInfoInput)
def get_hotel_info_tool(information_type: str) -> str:
    """Provides specific hotel information such as pool hours, gym, breakfast, or check-in/out times."""
    it = information_type.lower()
    if "pool" in it and "hour" in it:
        return "🏊 Pool hours: 6 AM – 10 PM."
    elif "gym" in it:
        return "💪 Gym is on 3rd floor. Open 24/7."
    elif "breakfast" in it:
        return "🍳 Breakfast: 7 AM – 10 AM in dining hall."
    elif "check-in" in it:
        return "Check-in time: 3:00 PM."
    elif "check-out" in it:
        return "Check-out time: 11:00 AM."
    return "Information type not found. Try asking about pool, gym, or breakfast."

@tool(args_schema=GetRoomDetailsInput)
def get_room_details_tool(guest_name: str, room_number: int) -> str:
    """Fetches room details such as type, view, and amenities for a specific guest and room number."""
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, "rooms.csv"))
        room = df[df["room_number"] == room_number].iloc[0]
        return (
            f"Room {room_number} for {guest_name}:\n"
            f"- Type: {room['room_type']}\n"
            f"- View: {room['view']}\n"
            f"- Amenities: {room['amenities']}"
        )
    except Exception:
        return f"Room details for {room_number} not found."