import pandas as pd
from langchain.tools import tool

@tool
def get_media_tool(room_type: str) -> str:
    """Provides links to pictures or videos of rooms and amenities."""
    try:
        df = pd.read_csv("data/social_media.csv")
        media_info = df[df["room_type"] == room_type].iloc[0]
        return f"Here is a {media_info['media_type']} of a {room_type} room: {media_info['url']}"
    except (FileNotFoundError, IndexError):
        return f"No media found for {room_type} rooms."