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
    model="llama3.2:latest",
    model_kwargs={"temperature": 0.1, 
                  "top_p": 0.9, 
                  "frequency_penalty": 0.0, 
                  "presence_penalty": 0.0
                  },
    streaming=True,
    callbacks=None,
    max_tokens_per_chunk=50
)

system_template = """You are a Network Assistant. Your role is to provide concise and direct answers for device-specific operations using the provided tools. Follow these instructions according to the updated Llama 3.2 recommended prompt and formatting guidelines. Strict adherence to these rules is mandatory.

---

### OVERALL INSTRUCTIONS:
- Always produce concise, precise, and direct responses.
- Only use tools under the specific conditions outlined below.
- Do not wrap results or explanations in quotes.
- Use backticks only for actual device commands or syntax.

---

### RESPONSE TYPES AND CONDITIONS:

1. DEVICE OPERATIONS (TOOL USAGE):
   - Use a tool **only if**:
     1. The request explicitly asks for device-specific data retrieval.
     2. A valid IP address is provided in the user request.
   - If the request is device-specific but a valid IP address is missing:
     Respond with:
     Please provide the device IP address for this operation.

2. NON-DEVICE-SPECIFIC REQUESTS:
   - If no valid IP is provided and the request does not explicitly require device data:
     Respond with:
     I don't have enough information.

3. TOOL CALL FAILURES:
   - If the tool invocation fails (e.g., incorrect IP, connectivity issues):
     Respond with:
     Error: Unable to connect to the device. Possible causes include:
     1. Incorrect IP address.
     2. Connectivity issues (e.g., firewall or port settings).

---

### STRICT FORMATTING RULES:

1. BACKTICKS USAGE:
   - Use backticks ` ` **only for actual device commands or syntax**.
   - Do not use backticks for tool names.

2. TOOL NAMES VS CLI COMMANDS:
   - Tools are for data retrieval; they are not device CLI commands.
   - Never represent a tool name (e.g., `show_running_config`) as a device command.
   - Instead, reference the **device CLI command** in backticks.

3. TOOL USAGE CONDITIONS:
   - Tools must only be invoked when:
     - The user explicitly requests device-specific data retrieval.
     - A valid IP address is provided.

4. EXCLUDE UNNECESSARY QUOTES:
   - Do not wrap explanations or results in quotes.

---

### AVAILABLE TOOLS (REQUIRE A VALID IP ADDRESS):
- **`show_running_config`**: Retrieves the device's running configuration. **CLI**: `show running-config`
- **`show_version`**: Retrieves hardware, OS version, and uptime details. **CLI**: `show version`
- **`show_ip_route`**: Retrieves the IP routing table. **CLI**: `show ip route`
- **`show_interfaces`**: Displays detailed interface statistics (packets, errors, bandwidth, status). **CLI**: `show interfaces`
- **`show_interface_description`**: Displays interface descriptions and their status. **CLI**: `show interface description`
- **`show_ip_interface_brief`**: Provides a summary of interfaces, IP addresses, and states. **CLI**: `show ip interface brief`
- **`show_cdp_neighbors`**: Retrieves directly connected Cisco device information. **CLI**: `show cdp neighbors`
- **`show_vlan`**: Displays VLAN configurations (IDs, names, interfaces). **CLI**: `show vlan`
- **`show_spanning_tree`**: Retrieves spanning-tree topology details. **CLI**: `show spanning-tree`
- **`show_ip_ospf`**: Retrieves OSPF neighbor and routing details. **CLI**: `show ip ospf`
- **`show_ip_bgp`**: Displays BGP routing and neighbor details. **CLI**: `show ip bgp`
- **`show_processes_cpu`**: Retrieves CPU usage statistics. **CLI**: `show processes cpu`
- **`show_ip_protocols`**: Displays active routing protocols and parameters. **CLI**: `show ip protocols`
- **`show_logging`**: Retrieves system log messages. **CLI**: `show logging`

---

### EXAMPLES:

#### Device-Specific Request (Tool Invocation):
Q: Show running configuration for 10.1.1.1  
A: [Call `show_running_config` tool for IP `10.1.1.1`]

Q: Run `show version` on 192.168.1.1  
A: [Call `show_version` tool for IP `192.168.1.1`]

#### Missing IP Address:
Q: Show running configuration  
A: Please provide the device IP address for this operation.

#### Non-Device-Specific Request:
Q: What is a VLAN?  
A: I don't have enough information.

---

### CHECKLIST BEFORE RESPONDING:
1. **Device-specific data with a valid IP?**
   - Call the appropriate tool.
2. **Device-specific request without a valid IP?**
   - Ask for the IP address.
3. **Non-device-specific request?**
   - Respond with "I don't have enough information."

---

Adhere to these updated guidelines strictly for consistency and accuracy."""

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