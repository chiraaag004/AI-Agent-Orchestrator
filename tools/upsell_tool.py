import pandas as pd
from langchain.tools import tool

@tool
def upsell_recommendation_tool(current_room: str) -> str:
    """Provides upsell recommendations for rooms and add-ons."""
    try:
        df = pd.read_csv("data/upsell_recommendations.csv")
        recommendation = df[df["current_room"] == current_room].iloc[0]
        return f"Would you like to upgrade to a {recommendation['recommendation']} for an additional ${recommendation['additional_cost']} per night?"
    except (FileNotFoundError, IndexError):
        return "No upsell recommendations available for your selection."