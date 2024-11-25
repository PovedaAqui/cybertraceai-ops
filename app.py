import uuid
from langchain_ollama import ChatOllama
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from tools import tools

# Initialize the model
llm = ChatOllama(model="llama3.1:8b", model_kwargs={"temperature": 0})

# Define system message template
system_template = """You are a helpful networking assistant. Use tools only when needed and provide a clear final answer based on the tool's output. 
Do not reuse a tool unless explicitly asked. You can show interface descriptions, routing tables, and interface status for Cisco devices.

When interpreting command outputs:
1. Do NOT repeat the raw output in your interpretation
2. Focus on providing meaningful insights about what the output shows
3. Highlight important details and their significance
4. Keep your interpretation concise and clear

If you encounter any errors, explain what might have caused them and suggest possible solutions."""

# Bind tools to the model
llm_with_tools = llm.bind_tools(tools)

# Create the react agent using prebuilt template
react_graph = create_react_agent(
    model=llm_with_tools,
    tools=tools,
    state_modifier=system_template,
    checkpointer=MemorySaver()
)

# Function to generate a unique thread_id
def generate_thread_id():
    return str(uuid.uuid4())

# Example usage of react agent graph
try:
    # Generate a unique thread_id for each invocation
    thread_id = generate_thread_id()
    config = {"configurable": {"thread_id": thread_id}}

    result = react_graph.invoke({
        "messages": [HumanMessage(content="Show routing table on 192.168.0.254")]
    }, config)
    
    # Print the thread_id and the raw output from the last message
    print(f"Thread ID: {thread_id}")
    print("Response:")
    print(result['messages'][-1].content)
except Exception as e:
    print(f"Error occurred: {str(e)}")
finally:
    wait_for_all_tracers()