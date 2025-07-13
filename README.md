# AI Agent Orchestrator

This project is a sophisticated, multi-agent AI orchestration framework built using LangGraph, LangChain, and Streamlit. It's designed to host and manage multiple, specialized AI agents, routing complex user queries to the correct agent and synthesizing the results into a coherent response.

The first agent implemented on this platform is the **AI Travel Companion**, which helps users with flight bookings, status checks, and support questions. The platform is built to be extensible, with an "AI Inquiry Call Agent" planned for future integration.

## ✨ Features

- **Multi-Agent Architecture:** Uses a `LangGraph` supervisor to route tasks to specialized agents (e.g., `flight_booking_manager`, `support_agent`).
- **Intent-Based Routing:** An LLM-based router classifies user queries into one or more intents to determine the correct agent(s) to invoke.
- **Tool Use:** Agents are equipped with specific tools (e.g., booking flights, checking status, FAQ lookup) to perform actions and retrieve information.
- **Multi-LLM Support:** Easily switch between different LLM providers (Gemini, OpenAI, Claude) via environment variables.
- **Multilingual Support:** Automatically detects the user's language, processes the query in English, and translates the final response back to the user's language.
- **Conversational Memory:** Maintains conversation history to handle follow-up questions and context.
- **Observability:** Integrated with Langfuse for detailed tracing and debugging of agent interactions.
- **Interactive UIs:** Includes a Streamlit-based chat application and an admin dashboard for monitoring agent traces.

## 🛠️ Tech Stack

- **Core Frameworks:** [LangChain](https://www.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/) for building stateful, multi-agent applications.
- **LLM Integrations:** Support for [Google Gemini](https://ai.google.dev/), [OpenAI](https://openai.com/), and [Anthropic Claude](https://www.anthropic.com/).
- **Frontend:** [Streamlit](https://streamlit.io/) for creating the interactive chat UI and admin dashboard.
- **Observability:** [Langfuse](https://langfuse.com/) for tracing, debugging, and monitoring agent performance.
- **Language & Data:** Python 3.10+ and [Pandas](https://pandas.pydata.org/) for data handling.

## 🏗️ Architecture

![AI Agent Orchestrator Architecture](assets/architecture-diagram.png)

The core of the agent is built with LangGraph, defining a stateful graph that orchestrates the flow of information:

1. **LLM Router:** The entry point. It analyzes the user's query to identify one or more intents (e.g., `flight_booking_manager`, `flight_information`).
2. **Agent Nodes:** For each identified intent, the graph routes the task to a specialized `ReActAgent` node. Each agent is equipped with a specific set of tools relevant to its function.
3. **Aggregator Node:** After an agent completes its task, its output is collected and appended to an aggregated response.
4. **Continuation Router:** This node checks if there are more intents to process. If so, it routes to the next agent; otherwise, it proceeds to the final step.
5. **Summarizer Node:** Once all tasks are complete, this node synthesizes the aggregated results into a single, user-friendly final response.
6. **Output Formatter:** The final response is formatted as an `AIMessage` and added to the conversation history.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- An API key for your chosen LLM provider (Google Gemini, OpenAI, or Anthropic).
- (Optional) Langfuse credentials for observability.

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/ai_hackathon.git
    cd ai_hackathon
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up your environment variables:**
    - Copy the example `.env` file:
        ```bash
        # On Windows
        copy .env.example .env
        # On macOS/Linux
        cp .env.example .env
        ```
    - Open the `.env` file and add your API keys and Langfuse credentials. See the Configuration section for more details.

## 🏃 Running the Applications

### 1. Interactive Chat App

This is the main user-facing application.

```bash
streamlit run apps/atca_app.py
```

### 2. Agent Admin Dashboard

This dashboard uses Langfuse traces to provide an overview of agent interactions.

```bash
streamlit run apps/dashboard.py
```

### 3. Command-Line Interface

For quick testing and debugging, you can run an interactive session in your terminal.

```bash
python test_graph.py
```

## 📂 Project Structure

```
ai_hackathon/
├── agents/         # Core agent logic, including the LangGraph definition, state, nodes, and routers.
├── apps/           # Streamlit applications (chat app, dashboard).
├── config/         # Configuration files, settings, and prompts.
│   └── prompts/    # Text files for different LLM prompts.
├── data/           # Static data, like the FAQ knowledge base.
├── tools/          # Individual tool definitions (e.g., book_flight, faq_tool).
├── utils/          # Helper utilities for loading tools and prompts.
├── workflows/      # High-level workflow logic (e.g., base agent, language helpers, router).
├── .env.example    # Environment variable template.
├── requirements.txt# Python dependencies.
└── test_graph.py   # Script for running the agent in the terminal.
```

## ⚙️ Configuration (.env file)

- **LLM_PROVIDER:** Set to gemini, openai, or claude.
- **MODEL_NAME:** Specify the model to use (e.g., gemini-pro, gpt-4, claude-3-sonnet-20240229).
- **GOOGLE_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY:** Provide the key for your selected provider.
- **LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST:** (Optional) Credentials for Langfuse tracing.
- **CONFIDENCE_THRESHOLD:** The confidence score (0-100) below which the router defaults to the "general" agent.
- **CONVERSATION_WINDOW_SIZE:** The number of recent messages to include in the agent's memory.

## 📊 Observability with Langfuse

This project is instrumented with Langfuse to provide deep insights into the agent's execution. When you run the agent (either via the Streamlit app or the test script), traces are automatically sent to your Langfuse project.

You can:
- Visualize the entire LangGraph flow for each query.
- Inspect the inputs and outputs of each node (LLM calls, tool executions).
- Debug errors and analyze latency and token usage.
- Use the provided Streamlit dashboard (`apps/dashboard.py`) for a high-level overview of traces.

