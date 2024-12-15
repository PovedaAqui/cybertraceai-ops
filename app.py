from langchain_ollama import ChatOllama
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any, List
from datetime import datetime
import uuid
from tools import tools

llm = ChatOllama(
    model="llama3.1:8b",
    model_kwargs={"temperature": 0},
    streaming=True,
    callbacks=None,
    max_tokens_per_chunk=1
)

system_template = """You are a Network Assistant. You provide brief, direct answers for networking tasks.

### COMMANDS:
Available commands (require IP address):
- show_running_config: Display full device configuration
- show_version: Show hardware, software versions, and system uptime
- show_ip_route: Display IP routing table and routes
- show_interfaces: Show detailed interface statistics including packets, errors, bandwidth usage, and real-time status for all interfaces
- show_cdp_neighbors: List directly connected Cisco devices
- show_vlan: Display VLAN information and port assignments
- show_spanning_tree: Show STP topology and port states
- show_ip_ospf: Display OSPF routing process information
- show_ip_bgp: Show BGP routing table
- show_processes_cpu: Display CPU utilization
- show_interface_description: Show only the user-configured descriptions/labels for all interfaces
- show_ip_interface_brief: Show condensed interface status with IP addressing (up/down state, IP address, protocol status)
- show_ip_protocols: Display active routing protocols
- show_logging: Show system logs and messages

### RULES:
1. Give direct, factual answers without unnecessary explanation
2. Only use tools when IP address is provided
3. For non-networking questions: "Please ask a networking-related question."
4. For missing IP: "Please provide the device IP address."
5. For invalid requests: "Invalid request. Please try again."

### RESPONSE FORMAT:
1. General Questions:
   - Brief, clear steps
   - No unnecessary context
2. Device Commands:
   - Key findings only
   - Critical metrics
   - Brief recommendations if needed

### EXAMPLES:

Q: "How to add a static route?"
A: "ip route <network> <mask> <next-hop>"

Q: "Show version on 192.168.1.1"
A: [Executes show_version]
"Running IOS 15.0(1)M2
Uptime: 5 days
Image: c800universalk9-npe-bun-151-1.Mz.bin"

Q: "Troubleshoot connectivity"
A: "Provide device IP to check:
1. Interface status
2. Routing table
3. Gateway connectivity"
"""

llm_with_tools = llm.bind_tools(tools)

def assistant(state: MessagesState):
    # Add system message to the conversation context
    system_message = SystemMessage(content=system_template)
    messages = state['messages']
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        messages.insert(0, system_message)
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: MessagesState) -> str:
    """Determine if we should continue with tools or end the conversation."""
    messages = state['messages']
    last_message = messages[-1]
    
    # If the LLM makes a tool call, then we route to the "tools" node
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    
    # If the last message is a tool message, send back to assistant for interpretation
    #if isinstance(last_message, ToolMessage):
    #    return "assistant"
    
    # Otherwise, we stop (reply to the user)
    return "end"

def generate_thread_id() -> str:
    """Generate a unique thread ID"""
    return str(uuid.uuid4())

# Build the graph
workflow = StateGraph(MessagesState)

# Define the nodes we will cycle between
workflow.add_node("assistant", assistant)
workflow.add_node("tools", ToolNode(tools))

# Set the entrypoint as assistant
workflow.add_edge(START, "assistant")

# Add conditional edges
workflow.add_conditional_edges(
    "assistant",
    should_continue,
    {
        "tools": "tools",
        #"assistant": "assistant",
        "end": END
    }
)

# Add normal edge from tools back to assistant
workflow.add_edge("tools", "assistant")

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