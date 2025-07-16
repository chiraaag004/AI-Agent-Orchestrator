from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import List
import pandas as pd

# --- Input Schemas ---

class LocalRecommendationsInput(BaseModel):
    """Input for providing local recommendations."""
    guest_name: str = Field(description="Name of the guest requesting recommendations.")
    preferences: List[str] = Field(description="List of guest preferences or interests (e.g., ['fine dining', 'live music']).")

class FindNearbyAttractionsInput(BaseModel):
    """Input for finding nearby attractions."""
    location: str = Field(description="Hotel name or address.")
    interests: List[str] = Field(description="List of interests (e.g., ['parks', 'museums']).")
    max_distance: float = Field(description="Max distance in miles.")

# --- Tool Functions ---

@tool(args_schema=LocalRecommendationsInput)
def provide_local_recommendations_tool(guest_name: str, preferences: List[str]) -> str:
    """Provides local recommendations based on guest preferences."""
    try:
        df = pd.read_csv("data/local_recommendations.csv")
    except FileNotFoundError:
        return "📂 local_recommendations.csv not found."

    matches = df[df["preference"].isin(preferences)]

    if matches.empty:
        return f"No recommendations found for preferences: {', '.join(preferences)}"

    recommendations = "\n".join(f"- {row['recommendation']}" for _, row in matches.iterrows())
    return f"Recommendations for {guest_name} based on preferences ({', '.join(preferences)}):\n{recommendations}"

@tool(args_schema=FindNearbyAttractionsInput)
def find_nearby_attractions_tool(location: str, interests: List[str], max_distance: float) -> str:
    """Finds nearby attractions based on location and interests, using mock data."""
    try:
        df = pd.read_csv("data/attractions.csv")
    except FileNotFoundError:
        return "📂 attractions.csv not found."

    results = df[
        (df["location"].str.lower() == location.lower()) &
        (df["type"].isin(interests)) &
        (df["distance"] <= max_distance)
    ]

    if results.empty:
        return f"No nearby attractions found within {max_distance} miles for interests: {', '.join(interests)}."

    return "Nearby attractions:\n" + "\n".join(
        f"- {row['name']} ({row['distance']} mi, {row['type']})"
        for _, row in results.iterrows()
    )
