import os
import csv
import random
import pandas as pd
from datetime import datetime
from langchain.tools import tool
from pydantic import BaseModel, Field

# --- Data Directory ---
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def safe_append_to_csv(file_path, row_dict, fieldnames):
    file_exists = os.path.exists(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_dict)

# --- Informational Tool ---

class LocalTransportInput(BaseModel):
    """Input for getting local transportation options."""
    location: str = Field(description="Hotel name or neighborhood.")
    transport_type: str = Field(description="Type of transport (e.g., 'taxi', 'metro', 'bus').")

@tool(args_schema=LocalTransportInput)
def local_transport_tool(location: str, transport_type: str) -> str:
    """Provides local transport options from mock data."""
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, "local_transport.csv"))
    except FileNotFoundError:
        return "📂 local_transport.csv not found."

    filtered = df[
        (df["location"].str.lower() == location.lower()) &
        (df["transport_type"].str.lower() == transport_type.lower())
    ]

    if filtered.empty:
        return f"No {transport_type} info found at {location}."

    return "\n".join(
        f"- {row['name']} ({row['description']})"
        for _, row in filtered.iterrows()
    )

# --- Booking Tool ---

class BookTransportInput(BaseModel):
    """Input for booking a local transport option."""
    guest_name: str = Field(description="Name of the guest booking transport.")
    transport_type: str = Field(description="Type of transport to book (e.g., 'taxi', 'shuttle').")
    pickup_time: str = Field(description="Requested pickup time (HH:MM).")
    destination: str = Field(description="Destination for the ride.")

@tool(args_schema=BookTransportInput)
def book_local_transport_tool(guest_name: str, transport_type: str, pickup_time: str, destination: str) -> str:
    """Books local transport for a guest and logs the booking in CSV."""
    booking_id = "TRN-" + "".join(str(random.randint(0, 9)) for _ in range(6))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = {
        "Timestamp": timestamp,
        "Booking ID": booking_id,
        "Guest Name": guest_name,
        "Transport Type": transport_type,
        "Pickup Time": pickup_time,
        "Destination": destination
    }

    csv_path = os.path.join(DATA_DIR, "transport_bookings.csv")
    safe_append_to_csv(csv_path, row, fieldnames=row.keys())

    return (
        f"✅ Transport booked for {guest_name}:\n"
        f"- Type: {transport_type.title()}\n"
        f"- Pickup Time: {pickup_time}\n"
        f"- Destination: {destination}\n"
        f"- Booking ID: {booking_id}"
    )
