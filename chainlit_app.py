import chainlit as cl
from app import react_graph, generate_thread_id
from langchain_core.messages import HumanMessage
from langchain.callbacks.tracers.langchain import wait_for_all_tracers

# Store settings that might be reused
WELCOME_MESSAGE = """👋 Hello! I'm your Cisco networking assistant. I can help you with:

- Checking interface descriptions
- Viewing routing tables
- Checking interface status

Please provide the device IP and your query."""

@cl.on_chat_start
async def start():
    """Initialize the chat session with a welcome message."""
    # Generate and store thread ID
    cl.user_session.set("thread_id", generate_thread_id())
    
    # Send welcome message
    await cl.Message(content=WELCOME_MESSAGE).send()

@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and generate responses."""
    try:
        print(f"[DEBUG] Received message: {message.content}")
        print(f"[DEBUG] Message ID: {message.id}")
        print(f"[DEBUG] Message author: {message.author}")
        
        # Get thread ID and prepare config
        thread_id = cl.user_session.get("thread_id")
        print(f"[DEBUG] Thread ID: {thread_id}")
        
        config = {"configurable": {"thread_id": thread_id}}
        msg_state = {"messages": [HumanMessage(content=message.content)]}
        
        # Process message and get response
        print("[DEBUG] Calling react_graph.ainvoke")
        result = await react_graph.ainvoke(msg_state, config)
        response = result['messages'][-1].content
        print(f"[DEBUG] Got response: {response}")
        
        # Send the final response
        print("[DEBUG] Sending final response")
        await cl.Message(content=response).send()
            
    except Exception as e:
        print(f"[DEBUG] Error occurred: {str(e)}")
        print(f"[DEBUG] Error type: {type(e)}")
        await cl.Message(
            content=f"❌ An error occurred: {str(e)}", 
            author="Error"
        ).send()
    finally:
        print("[DEBUG] Executing finally block")
        wait_for_all_tracers()