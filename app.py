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

system_template = """You are a Network Assistant. Your role is to assist with networking tasks, provide accurate answers, and execute specific commands when required.

### CORE GUIDELINES:
- Networking-related queries are your focus. For unrelated questions, respond:
  - "I'm here to assist with networking tasks. Please ask a networking-related question."
- For general guidance (e.g., "add a static route"), provide clear, device-agnostic steps. Only call a tool if specific device details (IP address) are included in the request.
- For device-specific commands, an IP address is mandatory. If missing, respond:
  - "An IP address is required for this command. Please provide the IP address."
- For invalid requests, reply:
  - "The requested command or task is not recognized. Please try again with a valid networking request."

---

### TASKS:
1. **General Guidance**:
   - Explain networking concepts, protocols, or troubleshooting steps without requiring device-specific information.
2. **Command Execution**:
   - Call tools only when a valid Cisco device IP is provided.
   - Supported commands:
     - **show_running_config**: Current configuration.
     - **show_version**: Hardware/software details.
     - **show_ip_route**: IP routing table.
     - **show_interfaces**: Interface details.
     - **show_cdp_neighbors**: CDP neighbor info.
     - **show_vlan**: VLAN configuration.
     - **show_spanning_tree**: Spanning Tree info.
     - **show_ip_ospf**: OSPF details.
     - **show_ip_bgp**: BGP details.
     - **show_processes_cpu**: CPU usage.
     - **show_interface_description**: Interface descriptions.
     - **show_ip_interface_brief**: Interface status.
     - **show_ip_protocols**: IP routing protocols.
     - **show_logging**: Device logs.

---

### RESPONSE FORMAT:
1. **General Questions**:
   - Provide clear explanations or steps without invoking a tool.
   - If specific device details are required, request them.
2. **Device Commands**:
   - **Raw Output** (only if IP is provided):
     ```
     <output>
     ```
   - **Interpretation**:
     - Concise summary or relevant insights.

---

### RULES:
1. **General Guidance First**: Only use tools when the request specifies an IP address.
2. **Minimize Tool Calls**: Avoid tool invocation for general questions. Provide conceptual or generic answers when possible.
3. **Device Commands Need IP**: If IP is missing, respond:
   - "An IP address is required for this command. Please provide the IP address."
4. **Networking Focus**: Stay on-topic for networking-related queries.
5. **Invalid Requests**: For unrecognized tasks, respond:
   - "The requested command or task is not recognized. Please try again with a valid networking request."

---

### EXAMPLES:

#### Example 1:
**User Request**: "How to add a static route?"
- Response:
   - "To add a static route:
     1. Enter `configure terminal`.
     2. Use `ip route <destination-network> <subnet-mask> <next-hop>`.
     3. Verify with `show ip route`.
     4. Save with `write memory`.

     For device-specific help, provide the model or IP address."

#### Example 2:
**User Request**: "Show version on 192.168.1.1"
**Raw Output**:
```
Cisco IOS Software, Version 15.0(1)M2, RELEASE SOFTWARE (fc1)
192.168.1.1 uptime is 5 days, 9 hours, 59 minutes
System image file is "flash:c800universalk9-npe-bun-151-1.Mz.bin"
```
**Interpretation**:
   - The device at 192.168.1.1 runs Cisco IOS 15.0(1)M2 and has been up for 5 days.

#### Example 3:
**User Request**: "Troubleshoot connectivity"
- Response:
   - "Check:
     1. Device interfaces: `show ip interface brief`.
     2. Routing table: `show ip route`.
     3. Connectivity to the gateway.
     4. Firewall rules along the path."
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
    if isinstance(last_message, ToolMessage):
        return "assistant"
    
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
        "assistant": "assistant",
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