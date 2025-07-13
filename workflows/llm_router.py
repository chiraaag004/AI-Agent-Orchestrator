from langchain.prompts import PromptTemplate
from config.llm_loader import load_llm
from config.settings import CONFIDENCE_THRESHOLD, ROUTER_INTENTS
import json
import os
import re
import logging

PROMPT_PATH = "config/prompts/router_prompt.txt"

# Load prompt dynamically from file
def load_prompt():
    with open(PROMPT_PATH, "r") as f:
        return PromptTemplate.from_template(f.read())

prompt = load_prompt()
llm = load_llm()

def route_intent(state: dict) -> dict:
    """
    Routes the user input to the correct workflow based on intent classification.

    Args:
        state (dict): The current state of the graph.

    Returns:
        dict: The updated state with 'intent' and 'confidence' keys.
    """
    messages = state.get("messages", [])
    if not messages:
        # Should not happen in a normal flow, but good practice to handle
        return {"intents": ["general"], "confidence": 0, "processed_intents": [], "aggregated_output": ""}
    user_input = messages[-1].content
    try:
        formatted_prompt = prompt.format(intents=json.dumps(ROUTER_INTENTS), input=user_input)
        raw_response = llm.invoke(formatted_prompt).content

        # Use a regular expression to extract the JSON object from the LLM's response.
        # This is more robust than string stripping as it finds the JSON block
        # regardless of surrounding text or markdown fences.
        json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if not json_match:
            # If no JSON is found, we can raise an error to be caught by the except block.
            raise json.JSONDecodeError("No JSON object found in LLM response", raw_response, 0)

        clean_json_str = json_match.group(0)
        parsed = json.loads(clean_json_str)
        raw_intents = parsed.get("intents", ["general"])
        confidence_val = parsed.get("confidence", 0)
        confidence = int(confidence_val) if str(confidence_val).isdigit() else 0

        # Validate that the returned intents are valid options. This makes the router
        # more robust against the LLM hallucinating an intent not in the list.
        validated_intents = [intent for intent in raw_intents if intent in ROUTER_INTENTS]

        if confidence < CONFIDENCE_THRESHOLD or not validated_intents:
            intents = ["general"]
        else:
            intents = validated_intents

        return {
            "intents": intents,
            "confidence": confidence,
        }

    except Exception as e:
        logging.error(f"Error in LLM router: {e}", exc_info=True)
        return {
            "intents": ["general"],
            "confidence": 0,
            "router_error": str(e),
        }
