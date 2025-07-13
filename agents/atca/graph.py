# agents/atca/graph.py
from langgraph.graph import StateGraph, END

# Local imports for the supervisor agent components
from .state import AgentState
from .nodes import aggregator_node, create_agent_runner, summarizer_node
from .routers import initial_router, continuation_router

# Workflow-level imports
from workflows.llm_router import route_intent
from workflows.formatter import format_output
from config.settings import ROUTER_INTENTS, AGENT_TOOL_MAPPING

# 1. Build LangGraph
graph = StateGraph(AgentState)

# 2. Add nodes to the graph
graph.add_node("llm_router", route_intent)
graph.add_node("aggregator", aggregator_node)
graph.add_node("summarizer", summarizer_node)
graph.add_node("final_output", format_output) # Renamed for clarity

# 3. Dynamically create a node for each defined agent capability
for agent_name, tool_names in AGENT_TOOL_MAPPING.items():
    graph.add_node(agent_name, create_agent_runner(agent_name, tool_names))
    graph.add_edge(agent_name, "aggregator")

# 4. Wire the graph together
graph.set_entry_point("llm_router")

# The first router decides which agent to run first.
# The map must include all possible outputs from the initial_router.
# This map is now derived directly from the single source of truth.
initial_route_map = {agent_name: agent_name for agent_name in AGENT_TOOL_MAPPING.keys()}
graph.add_conditional_edges("llm_router", initial_router, initial_route_map)

# The continuation router decides whether to run another agent or finish.
continuation_route_map = {agent_name: agent_name for agent_name in AGENT_TOOL_MAPPING.keys()}
continuation_route_map["FINISH"] = "summarizer"
graph.add_conditional_edges(
    "aggregator",
    continuation_router,
    continuation_route_map
)

graph.add_edge("summarizer", "final_output")
graph.add_edge("final_output", END)

# 5. Export LangGraph as an executable object
travel_graph = graph.compile()
