import pandas as pd
from langchain.tools import tool
from datetime import datetime

@tool
def festival_promotion_tool(month: str = None) -> str:
    """Checks for festival-themed promotions."""
    if month is None:
        month = datetime.now().strftime("%B")
    try:
        df = pd.read_csv("data/festivals.csv")
        promotion = df[df["month"].str.lower() == month.lower()].iloc[0]
        return f"This month, we are celebrating {promotion['festival']}! {promotion['promotion']}."
    except (FileNotFoundError, IndexError):
        return "No special promotions this month."