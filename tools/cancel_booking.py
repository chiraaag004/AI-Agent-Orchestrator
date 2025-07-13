from langchain.tools import tool
from pydantic import BaseModel, Field

class CancelBookingInput(BaseModel):
    """Input for the cancel booking tool."""
    booking_id: str = Field(description="The booking confirmation number, which typically looks like 'BKG-123-XYZ'.")

@tool(args_schema=CancelBookingInput)
def cancel_booking_tool(booking_id: str) -> str:
    """
    Use this tool to cancel a flight or hotel booking when you have a booking ID.
    Do not use this tool if you do not have a booking ID.
    """
    return f"✅ Booking {booking_id} has been cancelled. Refund will be processed within 3–5 business days."
