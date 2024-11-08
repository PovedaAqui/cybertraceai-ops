from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import StructuredTool
from langgraph.checkpoint.memory import MemorySaver
from netmiko import ConnectHandler

llm = ChatOllama(model="llama3.1:8b",
                  model_kwargs={"temperature": 0})

parser = StrOutputParser()

system_template = """You are a helpful assistant. When using tools, always provide a final answer based on the tool's output.
After using a tool, do not use it again unless explicitly asked to do so."""
prompt_template = ChatPromptTemplate([
    ("system", system_template),
    ("human", "{text}"),
])

def multiply(a: int, b: int) -> int:
    """Multiplies a and b."""
    return a * b

def show_interface_description(device_ip: str, username: str, password: str) -> str:
    """Executes 'show vlan brief' command on a Cisco device."""
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

tools = [StructuredTool.from_function(show_interface_description)]
llm_with_tools = llm.bind_tools(tools)

def assistant(state: MessagesState):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")
memory = MemorySaver()
react_graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "123"}}

try:
    result1 = react_graph.invoke({"messages": [HumanMessage(content="Show interface description on 192.168.0.254 username cisco password cisco")]}, config)
    #result2 = react_graph.invoke({"messages": [HumanMessage(content="Explain the output of the previous command.")]}, config)
    print(result1)
    #print(result2)
except Exception as e:
    print(f"Error occurred: {str(e)}")
    raise
finally:
    wait_for_all_tracers()