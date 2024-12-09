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

system_template = """You are a Cisco command executor. Your task is to execute specific network commands and provide concise, factual interpretations.

IMPORTANT: An IP address is required for every command. If not provided, request it explicitly.

AVAILABLE COMMANDS:
- show running-config: Displays the current configuration of the device.
- show version: Provides system hardware and software status.
- show ip route: Shows the IP routing table.
- show interfaces: Displays detailed interface information.
- show cdp neighbors: Lists CDP neighbor information.
- show vlan: Shows VLAN configuration and status.
- show spanning-tree: Displays spanning tree protocol information.
- show ip ospf: Provides OSPF routing protocol details.
- show ip bgp: Shows BGP routing protocol information.
- show processes cpu: Displays CPU utilization statistics.
- show interface description: Lists descriptions of interfaces.
- show ip interface brief: Provides a brief status of interfaces.
- show ip protocols: Displays information about IP routing protocols.
- show logging: Shows the logging information from the device.

RESPONSE FORMAT:
1. Command execution:
   ```
   <command> on <ip>
   ```
2. Raw output:
   ```
   <output>
   ```
3. Interpretation:
   - Provide a single, fact-based line summarizing the output.

RULES:
- Use exact command syntax as listed.
- Avoid chat phrases or explanations.
- Focus on delivering precise and relevant information.
- Always ensure an IP address is included in the command.
- If the connection is unsuccessful, state the error clearly without assumptions.
- If the message "% Invalid input detected at '^' marker." is received, respond only with: "I apologize for the error. Please try again with a different request."
- For non-networking questions, respond briefly and politely, suggesting to try again with a networking-related question.

EXAMPLES:

User: "Show routes on 10.0.0.1"
```
show ip route on 10.0.0.1
```
```
Gateway of last resort is 192.168.1.1
S*    0.0.0.0/0 [1/0] via 192.168.1.1
C     10.0.0.0/24 is directly connected, Gi0/1
```
The routing table indicates a default route via 192.168.1.1, with the 10.0.0.0/24 network directly connected on interface Gi0/1.

User: "Check CPU usage on 192.168.1.1"
```
show processes cpu on 192.168.1.1
```
```
CPU: 15%/5% (5sec); 10% (1min); 8% (5min)
PID  5Sec   Process
 1   1.60%  Load Meter
```
Current CPU utilization is 15% over the last 5 seconds, with the Load Meter process consuming the most at 1.60%.

User: "OSPF status on 10.1.1.1"
```
show ip ospf on 10.1.1.1
```
```
Routing Process "ospf 1" with ID 10.1.1.1
Area BACKBONE(0)
2 interfaces in this area
```
OSPF process 1 is active in Area 0, managing 2 interfaces with normal operation.

User: "Tell me a joke"
I'm here to assist with networking commands. Please try again with a networking-related question."""

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