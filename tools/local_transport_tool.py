from langchain.tools import tool
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime
import random
import os

# --- Informational Tool ---

class LocalTransportInput(BaseModel):
    """Input for getting local transportation options."""
    location: str = Field(description="Hotel name or neighborhood.")
    transport_type: str = Field(description="Type of transport (e.g., 'taxi', 'metro', 'bus').")

@tool(args_schema=LocalTransportInput)
def local_transport_tool(location: str, transport_type: str) -> str:
    """Provides local transport options from mock data."""
    try:
        df = pd.read_csv("data/local_transport.csv")
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

    booking_id = "TRN-" + "".join([str(random.randint(0, 9)) for _ in range(6)])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    booking = {
        "Timestamp": timestamp,
        "Booking ID": booking_id,
        "Guest Name": guest_name,
        "Transport Type": transport_type,
        "Pickup Time": pickup_time,
        "Destination": destination
    }

    # Ensure directory exists
    os.makedirs("data", exist_ok=True)
    csv_path = "data/transport_bookings.csv"

    # Append booking to CSV
    df = pd.DataFrame([booking])
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)

    return (
        f"✅ Transport booked for {guest_name}:\n"
        f"- Type: {transport_type.title()}\n"
        f"- Pickup Time: {pickup_time}\n"
        f"- Destination: {destination}\n"
        f"- Booking ID: {booking_id}"
    )

