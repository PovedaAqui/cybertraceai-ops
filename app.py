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

llm = ChatOllama(model="llama3.1:8b",
                 model_kwargs={"temperature": 0})

system_template = """You are a helpful networking assistant specialized in Cisco networking. 

For networking related questions:
1. Use tools when needed to check interface descriptions, routing tables, and interface status
2. Provide clear interpretations of command outputs without repeating raw data
3. Focus on meaningful insights and highlight important details
4. Keep responses concise and clear

For non-networking questions:
1. Politely explain that you are a networking specialist and can help with networking-related queries
2. Provide examples of questions you can help with (e.g., "You can ask me about network interfaces, routing tables, or device status")
3. Do not return empty responses or parameter dictionaries

If you encounter any errors, explain what might have caused them and suggest possible solutions."""

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
try:
    # Generate a unique thread ID for each conversation
    config = {"configurable": {"thread_id": generate_thread_id()}}
    
    result1 = react_graph.invoke({
        "messages": [HumanMessage(content="Show routing table on 192.168.0.254")]
    }, config)
    print(result1['messages'][-1].content)
    
except Exception as e:
    print(f"Error occurred: {str(e)}")
    raise
finally:
    wait_for_all_tracers()