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
    processing_msg = None
    try:
        # Get thread ID and prepare config
        thread_id = cl.user_session.get("thread_id")
        config = {"configurable": {"thread_id": thread_id}}
        
        # Prepare message state
        msg_state = {"messages": [HumanMessage(content=message.content)]}
        
        # Show processing status
        processing_msg = await cl.Message(content="🔄 Processing...").send()
        
        # Process message and get response
        result = react_graph.invoke(msg_state, config)
        response = result['messages'][-1].content
        
        # Send response
        await cl.Message(content=response).send()
        
    except Exception as e:
        # Send error message
        await cl.Message(
            content=f"❌ An error occurred: {str(e)}", 
            author="Error"
        ).send()
        
    finally:
        # Cleanup
        if processing_msg:
            await processing_msg.remove()
        # Handle tracers without awaiting
        wait_for_all_tracers()  # Removed await since this is not an async function