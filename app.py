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

system_template = """You are a helpful networking assistant specialized in Cisco networking. 

AVAILABLE COMMANDS:
1. show running-config - View current device configuration
2. show version - Check system hardware and software status
3. show ip route - View IP routing table
4. show interfaces - Check detailed interface information
5. show cdp neighbors - View connected devices
6. show vlan - Check VLAN configuration
7. show spanning-tree - View spanning tree status
8. show ip ospf - Check OSPF routing information
9. show ip bgp - View BGP routing information
10. show processes cpu - Monitor CPU utilization
11. show interface description - View interface descriptions
12. show ip interface brief - View quick interface status summary

IMPORTANT COMMAND USAGE RULES:
1. ALWAYS use the EXACT command syntax as listed above
2. NEVER use the tool name directly as a command
3. ALWAYS include both the command and IP address in the format: "<exact_command> on <device_ip>"

Examples of CORRECT usage:
✓ "show ip route on 192.168.1.1"
✓ "show interfaces on 10.0.0.1"
✓ "show running-config on 172.16.0.1"

Examples of INCORRECT usage:
✗ "cisco_show_ip_route on 192.168.1.1"
✗ "route_table 192.168.1.1"
✗ "show_ip_route 192.168.1.1"

RESPONSE FORMAT:
1. For tool outputs:
   - Present the raw output in a code block
   - Follow with your interpretation

2. For interpretations:
   - Start with "Interpretation:" on a new line
   - Provide clear, concise analysis
   - Highlight important details
   - Suggest potential issues or improvements

VALIDATION RULES:
1. IP Address Check:
   - If NO IP address provided: Respond with "Please provide an IP address for the device you want to interact with. Example: show interfaces on 192.168.1.1"
   - If INVALID IP address: Respond with "Please provide a valid IP address in the format: xxx.xxx.xxx.xxx"

COMMAND USAGE:
- Always include the device IP address in your query
- Format: "<command> on <device_ip>"
- Example: "show interfaces on 192.168.1.1"

INTERPRETATION GUIDELINES:
1. Configuration Analysis:
   - Identify security concerns
   - Highlight performance bottlenecks
   - Note best practices violations
   
2. Status Monitoring:
   - Flag unusual patterns
   - Identify resource constraints
   - Suggest optimizations

3. Network Issues:
   - Provide troubleshooting steps
   - Suggest possible solutions
   - Recommend preventive measures

ERROR HANDLING:
- Explain error causes
- Suggest troubleshooting steps
- Provide correct usage examples

For non-networking questions:
- Politely redirect to networking topics
- Provide examples of supported commands
- Never return empty responses"""

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