from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import StructuredTool
from langgraph.checkpoint.memory import MemorySaver

llm = ChatBedrock(model="anthropic.claude-3-haiku-20240307-v1:0",
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

tools = [StructuredTool.from_function(multiply)]
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
    result1 = react_graph.invoke({"messages": [HumanMessage(content="Multiply 3 times 3.")]}, config)
    result2 = react_graph.invoke({"messages": [HumanMessage(content="Multiply that by 4.")]}, config)
    print(result1)
    print(result2)
except Exception as e:
    print(f"Error occurred: {str(e)}")
    raise
finally:
    wait_for_all_tracers()