from langchain_ollama import ChatOllama
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, Any, TypedDict, List
from datetime import datetime
from tools import tools

llm = ChatOllama(model="llama3.1:8b",
                 model_kwargs={"temperature": 0})

system_template = """You are a helpful networking assistant. Use tools only when needed and provide a clear final answer based on the tool's output. 
Do not reuse a tool unless explicitly asked. You can show interface descriptions, routing tables, and interface status for Cisco devices.

When interpreting command outputs:
1. Do NOT repeat the raw output in your interpretation
2. Focus on providing meaningful insights about what the output shows
3. Highlight important details and their significance
4. Keep your interpretation concise and clear

If you encounter any errors, explain what might have caused them and suggest possible solutions."""

llm_with_tools = llm.bind_tools(tools)

class OutputFormat(TypedDict):
    command_output: str
    interpretation: str
    timestamp: str

class OutputState(TypedDict):
    messages: List[AIMessage]
    formatted_output: OutputFormat

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

def format_output(state: MessagesState) -> OutputState:
    """Formats the final response according to the schema."""
    messages = state['messages']
    
    # Get the current timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Initialize variables
    tool_output = "No tool output available"
    interpretation = "No interpretation available"
    
    # Find the tool message and the last AI interpretation
    for msg in messages:
        if isinstance(msg, ToolMessage):  # Get the raw tool output
            tool_output = msg.content
        elif isinstance(msg, AIMessage) and msg.content and not msg.content.startswith('Command Output:'):
            # Get the last AI message that's not a formatted output
            interpretation = msg.content
    
    formatted_output = OutputFormat(
        command_output=tool_output,
        interpretation=interpretation,
        timestamp=current_time
    )
    
    # Create formatted message
    formatted_message = (
        f"Command Output:\n{formatted_output['command_output']}\n\n"
        f"Interpretation:\n{formatted_output['interpretation']}\n\n"
        f"Timestamp: {formatted_output['timestamp']}"
    )
    
    return {
        "messages": [AIMessage(content=formatted_message)],
        "formatted_output": formatted_output
    }

# Build the graph
builder = StateGraph(MessagesState, output=OutputState)
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
        "messages": [HumanMessage(content="Show routing table on 192.168.0.254")]
    }, config)
    print(result1['messages'][-1].content)
    
except Exception as e:
    print(f"Error occurred: {str(e)}")
    raise
finally:
    wait_for_all_tracers()