# **AI Agent Orchestrator**

This project is a sophisticated, multi-agent AI orchestration framework built using **LangGraph**, **LangChain**, and **Streamlit**. It's designed to host and manage multiple, specialized AI agents, routing complex user queries to the correct agent and synthesizing the results into a coherent response.

The first agent implemented on this platform is the **AI Travel Companion**, which helps users with flight bookings, status checks, and support questions. The platform is built to be extensible, with an **AI Inquiry Call Agent** planned for future integration.

---

## ✨ **Features**

- **Multi-Agent Architecture:**  
  Uses a `LangGraph` supervisor to route tasks to specialized agents (e.g., `flight_booking_manager`, `support_agent`).

- **Intent-Based Routing:**  
  An LLM-based router classifies user queries into one or more intents to determine the correct agent(s) to invoke.

- **Tool Use:**  
  Agents are equipped with specific tools (e.g., booking flights, checking itineraries, checking flight status, FAQ lookup) to perform actions and retrieve information.

- **Multi-LLM Support:**  
  Easily switch between different LLM providers (**Gemini**, **OpenAI**, **Claude**) via environment variables.

- **Multilingual Support:**  
  Automatically detects the user's language, processes the query in English, and translates the final response back to the user's language.

- **Hybrid Conversational Memory:**  
  Combines a short-term sliding window for immediate context with a long-term vector-based memory to recall important facts and preferences from earlier in the conversation.

- **Observability:**  
  Integrated with **Langfuse** for detailed tracing and debugging of agent interactions.

- **Multiple Interfaces:**  
  Interact with the agent via a web-based **Streamlit** chat, a command-line interface, or a WhatsApp/SMS interface powered by **Twilio** and **Flask**.

---

## 🛠️ **Tech Stack**

- **🧩 Core Frameworks:**  
  [LangChain](https://www.langchain.com/) & [LangGraph](https://langchain-ai.github.io/langgraph/)  
  *Build stateful, multi-agent applications with flexible orchestration.*

- **🤖 LLM Integrations:**  
  [Google Gemini](https://ai.google.dev/), [OpenAI](https://openai.com/), [Anthropic Claude](https://www.anthropic.com/)  
  *Easily switch providers via environment variables.*

- **💬 User Interfaces:**  
  [Streamlit](https://streamlit.io/) for interactive web chat and dashboards  
  [Flask](https://flask.palletsprojects.com/) & [Twilio](https://www.twilio.com/) for WhatsApp/SMS integration

- **🔎 Observability:**  
  [Langfuse](https://langfuse.com/)  
  *Trace, debug, and monitor agent performance and flows.*

- **🌐 Language & Data:**  
  Python 3.10+  
  [Pandas](https://pandas.pydata.org/) for data handling and export

---

## 🏗️ **Architecture**

![AI Agent Orchestrator Architecture](assets/architecture-diagram.png)

The core of the agent is built with **LangGraph**, defining a stateful graph that orchestrates the flow of information:

1. **LLM Router:**  
   The entry point. It analyzes the user's query to identify one or more intents (e.g., `flight_booking_manager`, `flight_information`).

2. **Agent Nodes:**  
   For each identified intent, the graph routes the task to a specialized `ReActAgent` node.  
   Each agent is equipped with a specific set of tools relevant to its function.

3. **Aggregator Node:**  
   After an agent completes its task, its output is collected and appended to an aggregated response.  
   The aggregator now ensures every output is returned as an `AIMessage` for downstream nodes and UI compatibility.

4. **Continuation Router:**  
   This node checks if there are more intents to process. If so, it routes to the next agent; otherwise, it proceeds to the final step.

5. **Summarizer Node:**  
   Once all tasks are complete, this node synthesizes the aggregated results into a single, user-friendly final response.

6. **Output Formatter:**  
   The final response is formatted as an `AIMessage` and added to the conversation history.

7. **Multi-Interface Support:**  
   The architecture supports interaction via Streamlit web chat, command-line, and WhatsApp/SMS (Twilio + Flask).

---

## 🚀 **Getting Started**

### **Prerequisites**

- **Python 3.10+**
- **API key** for your chosen LLM provider (Google Gemini, OpenAI, or Anthropic)
- *(Optional)* **Langfuse credentials** for observability
- *(Optional)* **Twilio credentials** for WhatsApp integration

---

### **Installation**

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
    - Open the `.env` file and add your API keys, Langfuse credentials, and (optionally) Twilio credentials.  
      See the **Configuration** section for more details.

---

## 🏃 **Running the Applications**

### **1. Interactive Chat App**

This is the main user-facing application.

```bash
streamlit run apps/atca_app.py
```

---

### **2. Agent Admin Dashboard**

This dashboard uses Langfuse traces to provide an overview of agent interactions.

```bash
streamlit run apps/dashboard.py
```

---

### **3. Command-Line Interface**

For quick testing and debugging, you can run an interactive session in your terminal.

```bash
python test_graph.py
```

---

### **4. WhatsApp Integration via Twilio**

Interact with the AI Agent Orchestrator via WhatsApp using Twilio and Flask.  
The integration is handled by the `twilio_app.py` application.

- **How it works:**  
  Incoming WhatsApp messages are received by Twilio, forwarded to your Flask app (`twilio_app.py`), processed by the agent, and the response is sent back to the user on WhatsApp.

- **To run the WhatsApp integration server:**
    ```bash
    python apps/twilio_app.py
    ```

- **Configuration:**  
  Make sure your `.env` file includes your Twilio credentials:
  ```
  TWILIO_ACCOUNT_SID=your_account_sid
  TWILIO_AUTH_TOKEN=your_auth_token
  TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
  ```

- **Setup:**  
  - Deploy the Flask app (`twilio_app.py`) on a public server or use [ngrok](https://ngrok.com/) for local development.
  - Configure your Twilio WhatsApp sandbox to forward incoming messages to your Flask endpoint.

---

## 📂 **Project Structure**

```
ai_hackathon/
├── agents/         # Core agent logic, including the LangGraph definition, state, nodes, and routers.
├── apps/           # Streamlit applications (chat app, dashboard), Flask Twilio WhatsApp app.
│   ├── **atca_app.py**     # Streamlit chat app (**main user interface**)
│   ├── **dashboard.py**    # Streamlit dashboard for **Langfuse traces**
│   └── **twilio_app.py**   # Flask app for **Twilio WhatsApp integration**
├── config/         # Configuration files, settings, and prompts.
│   └── prompts/    # Text files for different LLM prompts.
├── data/           # Mock data, like the FAQ knowledge base.
├── tools/          # Individual tool definitions (e.g., book_flight, itinerary_checker, flight_status_checker, faq_tool).
├── utils/          # Helper utilities for loading tools, prompts, and setting up memory.
├── workflows/      # High-level workflow logic (e.g., base agent, language helpers, router).
├── .env.example    # Environment variable template.
├── requirements.txt# Python dependencies.
└── test_graph.py   # Script for running the agent in the terminal.
```

---

## ⚙️ **Configuration (.env file)**

- **LLM_PROVIDER:** Set to `gemini`, `openai`, or `claude`.
- **MODEL_NAME:** Specify the model to use (e.g., `gemini-pro`, `gpt-4`, `claude-3-sonnet-20240229`).
- **GOOGLE_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY:** Provide the key for your selected provider.
- **LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST:** *(Optional)* Credentials for Langfuse tracing.
- **CONFIDENCE_THRESHOLD:** The confidence score (0-100) below which the router defaults to the "general" agent.
- **CONVERSATION_WINDOW_SIZE:** The number of recent messages to include in the agent's memory.

---

## 🧠 **Long-Term Memory**

Beyond the standard conversational window (`CONVERSATION_WINDOW_SIZE`), this project includes a mechanism for **long-term memory** to provide a more personalized and context-aware experience.

### **How It Works**

- **Saving Context:** Key pieces of information from the conversation (e.g., user preferences, booking details) are identified and saved to an in-memory FAISS vector store.
- **Embedding:** Each saved piece of information is converted into a numerical vector (an embedding).
- **Retrieval:** When a new query comes in, the agent searches the vector store for the most semantically similar memories.
- **Context Injection:** These relevant memories are injected back into the agent's prompt, allowing it to recall past details that are relevant to the current topic, even if they occurred much earlier in the conversation.

This setup is managed by `utils/memory_setup.py`.  
For production use, the in-memory FAISS store could be swapped with a persistent vector database like **ChromaDB** or a managed service.

---

## 📊 **Observability with Langfuse**

This project is instrumented with **Langfuse** to provide deep insights into the agent's execution.  
When you run the agent (either via the Streamlit app or the test script), traces are automatically sent to your Langfuse project.

You can:

- **Visualize** the entire LangGraph flow for each query.
- **Inspect** the inputs and outputs of each node (LLM calls, tool executions).
- **Debug** errors and analyze latency and token usage.
- Use the provided **Streamlit dashboard** (`apps/dashboard.py`) for a high-level overview of traces.
