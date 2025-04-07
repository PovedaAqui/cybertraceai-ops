from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Annotated, TypedDict
import uuid
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
# Import tools and shutdown logic from client.py
from client import tools

llm = ChatOllama(
    model="llama3.1:8b",
    model_kwargs={"temperature": 0.0, 
                  "top_p": 0.9, 
                  "frequency_penalty": 0.0, 
                  "presence_penalty": 0.0
                  },
    streaming=True,
    callbacks=None,
    max_tokens_per_chunk=50
)

system_template = """You are a Network Observability Assistant that uses SuzieQ tools to answer network state queries precisely.

THOUGHT PROCESS:
1. Understand the user's query and the specific network information needed.
2. Identify the appropriate SuzieQ table (e.g., device, interface, bgp, routes).
3. Choose the correct tool: 'run_suzieq_show' for detailed data or 'run_suzieq_summarize' for aggregated views.
4. Determine necessary filters (hostname, vrf, state, etc.) to narrow down the results.
5. Construct the tool call with the 'table' and optional 'filters' arguments.
6. Analyze the JSON response and formulate a clear answer for the user.

AVAILABLE TOOLS:

1.  **run_suzieq_show**: Retrieves detailed information from a specific SuzieQ table.
    *   `table` (String, Required): The SuzieQ table name (e.g., "device", "interface", "bgp").
    *   `filters` (Dictionary, Optional): Key-value pairs for filtering (e.g., { "hostname": "leaf01", "state": "up" }). Omit or use {} for no filters.
    *   Returns: JSON string with detailed results.

2.  **run_suzieq_summarize**: Provides a summarized overview of data in a SuzieQ table.
    *   `table` (String, Required): The SuzieQ table name to summarize (e.g., "device", "interface", "bgp").
    *   `filters` (Dictionary, Optional): Key-value pairs for filtering (e.g., { "hostname": "leaf01" }). Omit or use {} for no filters.
    *   Returns: JSON string with summarized results.

TOOL USAGE EXAMPLES:

*   Show all devices:
    `{ "table": "device" }` (using run_suzieq_show)
*   Show BGP neighbors for hostname 'spine01':
    `{ "table": "bgp", "filters": { "hostname": "spine01" } }` (using run_suzieq_show)
*   Show 'up' interfaces in VRF 'default':
    `{ "table": "interface", "filters": { "vrf": "default", "state": "up" } }` (using run_suzieq_show)
*   Summarize all devices:
    `{ "table": "device" }` (using run_suzieq_summarize)
*   Summarize BGP sessions by hostname 'spine01':
    `{ "table": "bgp", "filters": { "hostname": "spine01" } }` (using run_suzieq_summarize)
*   Summarize interface states in VRF 'default':
    `{ "table": "interface", "filters": { "vrf": "default" } }` (using run_suzieq_summarize)

QUERY GUIDELINES:
*   Be specific about the table you want to query.
*   Use filters to request data only for relevant devices, VRFs, states, etc.
*   Use `run_suzieq_summarize` for overviews and counts.
*   Use `run_suzieq_show` for detailed attribute information.

RESPONSE FORMAT:
1. Directly answer the user's query using the information retrieved from the tools.
2. Present the data clearly, often referencing the source table and filters used.
3. If applicable, suggest relevant follow-up questions.

Remember:
*   Only use the provided tools (`run_suzieq_show`, `run_suzieq_summarize`).
*   Ensure the 'table' parameter is always provided.
*   Format filters correctly as a dictionary if used.
"""

# server_params = StdioServerParameters( # Moved to client.py
#     command="uv",
#     args=[
#         "run",
#         "python",
#         # IMPORTANT: Ensure this path is correct for your system
#         r"C:\Users\Luis\Documents\Luis\suzieq-mcp\main.py"
#     ]
# )

# Define the state structure (simplified)
class State(TypedDict):
    messages: Annotated[list, add_messages]
    
# Bind tools to the LLM (only if tools were loaded)
if tools:
    llm_with_tools = llm.bind_tools(tools)
else:
    llm_with_tools = llm # Fallback to LLM without tools

def assistant(state: State):
    """Process messages with available tools."""
    # Add system message to the conversation context
    system_message = SystemMessage(content=system_template)
    messages = state['messages']
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        messages.insert(0, system_message)
    
    # Invoke the LLM (potentially with tools, depending on successful loading)
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: MessagesState) -> str:
    """Determine if we should continue with tools or end the conversation."""
    # Ensure state has 'messages' and it is not empty
    if 'messages' not in state or not state['messages']:
        return "end"  # Default to ending the conversation if no messages exist

    messages = state['messages']
    last_message = messages[-1]

    # Check if the last message is an AIMessage and has tool_calls
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # Otherwise, reply to the user
    return "end"

def generate_thread_id() -> str:
    """Generate a unique thread ID"""
    return str(uuid.uuid4())

# Build the graph
workflow = StateGraph(State)

# Define the nodes
workflow.add_node("assistant", assistant)
# Add tool node only if tools were successfully loaded
if tools:
    workflow.add_node("tools", ToolNode(tools))

# Set the entrypoint as assistant
workflow.add_edge(START, "assistant")

# Add conditional edges only if tools node exists
if tools:
    workflow.add_conditional_edges(
        "assistant",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    # Add normal edge from tools back to assistant
    workflow.add_edge("tools", "assistant")
else:
     # If no tools, assistant always goes to END
     workflow.add_edge("assistant", END)

# Initialize memory
memory = MemorySaver()
react_graph = workflow.compile(checkpointer=memory)

# Keep tracers waiting if used, shutdown is handled by atexit
wait_for_all_tracers()
print("Graph compiled. Setup complete. Application might run or wait for input.")
# Note: The script will now wait for exit to trigger the atexit cleanup.
# If this is meant to be a long-running server, ensure the main thread stays alive.
# If it's a script that should exit after setup, you might need explicit execution and exit logic.