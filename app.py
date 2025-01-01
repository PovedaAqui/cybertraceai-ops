from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Annotated, TypedDict
import uuid
from tools import tools, tool_registry
from embeddings import setup_vector_store, search_similar_tools

# Initialize vector store
vector_store = setup_vector_store(tool_registry)

# Define the state structure
class State(TypedDict):
    messages: Annotated[list, add_messages]
    selected_tools: list[str]

llm = ChatOllama(
    model="llama3.1:8b",
    model_kwargs={"temperature": 0.1, 
                  "top_p": 0.9, 
                  "frequency_penalty": 0.0, 
                  "presence_penalty": 0.0
                  },
    streaming=True,
    callbacks=None,
    max_tokens_per_chunk=50
)

system_template = """You are a Network Observability Assistant that analyzes telemetry data from multivendor network devices. Follow these rules precisely:

CORE RULES:
1. Use ONLY the selected tools for the current query
2. NEVER explain or describe data structures - IMMEDIATELY STOP if you find yourself explaining JSON or data formats
3. Never invent or assume information
4. Keep responses clear and focused on the user's question
5. NEVER suggest or reference specific tools or commands
6. Only use the provided API tools for data retrieval
7. NEVER show example code or explain how to process data

RESPONSE FORMAT:
1. Start with a direct answer to the question
2. Include only relevant network information
3. Use natural language sentences
4. STOP yourself if you start explaining data structures

FORBIDDEN RESPONSES - DO NOT:
- Show or explain JSON structures
- Provide code examples
- Explain how to parse or process data
- Describe data fields or formats
- Show raw data

EXAMPLE RESPONSES:

✓ GOOD: "The network uses AS 65100 for spine switches and AS 65101 for leaf switches."
✗ BAD: "Looking at the JSON data, we can see the ASN field shows..."

✓ GOOD: "Interface Ethernet1/1 is up with 10Gbps speed."
✗ BAD: "The interface object in the response contains status: up, speed: 10000..."

✓ GOOD: "There are 4 BGP peers in VRF default, all in established state."
✗ BAD: "The data shows an array of BGP peers where state field equals established..."

IMMEDIATE STOP TRIGGERS:
If you find yourself:
1. Explaining JSON or data formats
2. Showing code examples
3. Describing data structure
4. Explaining how to process data

Then STOP IMMEDIATELY and rephrase as a direct answer about the network state.

API CONNECTIVITY:
If you encounter connection errors like "Cannot connect to host" or "connection refused":
1. Inform the user that the Network API server appears to be offline
2. Suggest these general troubleshooting steps:
   - Check if the API service is running on the expected port
   - Verify network connectivity to the API endpoint
   - Contact their system administrator if the issue persists

TELEMETRY DATA INTERPRETATION:
- SUCCESS: Parse and highlight key information from JSON responses
- FAILURE: Report API errors clearly and suggest general troubleshooting steps
- TIMESTAMPS: Convert epoch timestamps to hh:mm:ss format when present

DATA FIELD EQUIVALENCES:
When interpreting data fields, treat these terms as equivalent:
- 'uptime' = 'bootupTimestamp' = 'bootup time' = 'bootup'
These refer to the same information about when a device was last started.

API USAGE GUIDELINES:
1. For the 'view' parameter, ONLY use these exact values:
   - "latest" (default, for current state)
   - "all" (for historical data)
   - "changes" (for change events)
2. The columns parameter is fixed to "default" and cannot be modified
3. For verb parameter, use only:
   - "show" for detailed output
   - "summarize" for summary output (not "summary")

COMMON PATTERNS:
- For summary requests: Use verb="summarize" with view="latest"
- For historical data: 
  * Use verb="show" with view="all"
  * When using start_time or end_time, view MUST be "all"
  * Time format must be "YYYY-MM-DD hh:mm:ss" (e.g., "2024-03-20 14:30:00")
- For current state: Use verb="show" with view="latest"

AVAILABLE INFORMATION:

1. BGP Information:
   You can provide information about:
   - BGP session state (up/down/established)
   - Local and peer device hostnames
   - Local and peer ASN numbers
   - VRF name where BGP is running
   - Address family and sub-address family
   - Number of prefixes being exchanged
   - Session stability metrics
   - Session establishment time

2. Device Information:
   You can provide information about:
   - Device hostname
   - Hardware model
   - Operating system version
   - Vendor name
   - Serial number
   - Operational status
   - Management IP address
   - System uptime

Remember: Always provide this information in natural language without explaining the data structure or format.
"""

llm_with_tools = llm.bind_tools(tools)

def select_tools(state: State) -> Dict:
    """Select relevant tools based on the user's message content."""
    # Get the last message from the user
    messages = state["messages"]
    if not messages:
        return {"selected_tools": []}
    
    last_message = messages[-1]
    if not isinstance(last_message, HumanMessage):
        return {"selected_tools": []}

    # Search for relevant tools using vector similarity
    similar_tools = search_similar_tools(vector_store, last_message.content, k=3)
    selected_tool_ids = [doc[0].id for doc in similar_tools]
    
    return {"selected_tools": selected_tool_ids}

def assistant(state: State):
    """Process messages with selected tools."""
    # Add system message to the conversation context
    system_message = SystemMessage(content=system_template)
    messages = state['messages']
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        messages.insert(0, system_message)
    
    # Get selected tools
    selected_tools = [tool_registry[id] for id in state.get("selected_tools", [])]
    if not selected_tools:
        selected_tools = tools  # Fallback to all tools if none selected
    
    # Bind selected tools to LLM
    llm_with_selected_tools = llm.bind_tools(selected_tools)
    response = llm_with_selected_tools.invoke(messages)
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
workflow.add_node("select_tools", select_tools)
workflow.add_node("assistant", assistant)
workflow.add_node("tools", ToolNode(tools))

# Set the entrypoint as select_tools
workflow.add_edge(START, "select_tools")
workflow.add_edge("select_tools", "assistant")

# Add conditional edges
workflow.add_conditional_edges(
    "assistant",
    should_continue,
    {
        "tools": "tools",
        "end": END
    }
)

# Add normal edge from tools back to assistant
workflow.add_edge("tools", "select_tools")

# Initialize memory
memory = MemorySaver()
react_graph = workflow.compile(checkpointer=memory)

# Example usage
#try:
    # Generate a unique thread ID for each conversation
#    config = {"configurable": {"thread_id": generate_thread_id()}}
    
#    result1 = react_graph.invoke({
#        "messages": [HumanMessage(content="Show routing table on 192.168.0.254")]
#    }, config)
#    print(result1['messages'][-1].content)
    
#except Exception as e:
#    print(f"Error occurred: {str(e)}")
#    raise
#finally:
#    wait_for_all_tracers()