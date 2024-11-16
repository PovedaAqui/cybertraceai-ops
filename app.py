from langchain_ollama import ChatOllama
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import StructuredTool
from langgraph.checkpoint.memory import MemorySaver
from netmiko import ConnectHandler
from typing import Dict, Any
import json
from datetime import datetime

llm = ChatOllama(model="llama3.1:8b",
                 model_kwargs={"temperature": 0})

system_template = """You are a helpful networking assistant. Use tools only when needed and provide a clear final answer based on the tool's output. 
Do not reuse a tool unless explicitly asked. You can show interface descriptions, routing tables, and interface status for Cisco devices.
When using tools, always provide the output in a clear, formatted way and explain what the output means.
If you encounter any errors, explain what might have caused them and suggest possible solutions."""

def show_interface_description(device_ip: str, username: str, password: str) -> str:
    """Executes 'show interface description' command on a Cisco device."""
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show interface description")
        return output 
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

def show_ip_route_cisco(device_ip: str, username: str, password: str) -> str:
    """Executes 'show ip route' command on a Cisco device to display the routing table."""
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show ip route")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

def show_ip_interface_brief(device_ip: str, username: str, password: str) -> str:
    """Executes 'show ip interface brief' command on a Cisco device to display interface status."""
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show ip interface brief")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

# Create structured tools from both functions
tools = [
    StructuredTool.from_function(show_interface_description),
    StructuredTool.from_function(show_ip_route_cisco),
    StructuredTool.from_function(show_ip_interface_brief)
]

llm_with_tools = llm.bind_tools(tools)

def assistant(state: MessagesState):
    # Add system message to the conversation context
    system_message = SystemMessage(content=system_template)
    # Get existing messages from state and add system message at the beginning if it's not already there
    messages = state['messages']
    # Ensure system message is included at the start of each conversation
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        messages.insert(0, system_message)
    # Invoke LLM with tools using updated messages (including system template)
    response = llm_with_tools.invoke(messages)
    # Return updated state with new response message added
    return {"messages": [response]}

def format_output(state: MessagesState):
    """Formats the final response to be more user-friendly and includes a timestamp."""
    # Extract the last message (which should be tool output or LLM response)
    messages = state['messages']
    last_message = messages[-1]
    
    # Check if it's an AIMessage (which comes from LLM) or tool output
    if isinstance(last_message, AIMessage):
        content = last_message.content
    else:
        content = "No valid response found."
    
    # Get the current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format the response with a timestamp
    formatted_response = (
        f"Timestamp: {current_time}\n"
        f"{content}\n"
    )
    
    # Add the formatted message as an AIMessage
    return {"messages": [AIMessage(content=formatted_response)]}

# Build the graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_node("format_output", format_output)

# Define the edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")
builder.add_edge("assistant", "format_output")
builder.add_edge("format_output", END)

# Initialize memory
memory = MemorySaver()
react_graph = builder.compile(checkpointer=memory)

# Configuration
config = {"configurable": {"thread_id": "123"}}

# Example usage
try:
    # You can now use either tool
    result1 = react_graph.invoke({
        "messages": [HumanMessage(content="Show interface brief on 192.168.0.254 username cisco password cisco")]
    }, config)
    print(result1['messages'][-1].content)
    
except Exception as e:
    print(f"Error occurred: {str(e)}")
    raise
finally:
    wait_for_all_tracers()