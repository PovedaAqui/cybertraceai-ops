import chainlit as cl
from app import react_graph, generate_thread_id
from langchain_core.messages import HumanMessage
from typing import Dict, Optional
import json # Added for potential future use with thread data


@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  # Simply return the default user object to allow access
  # You can add custom logic here to filter users if needed
  # based on raw_user_data or provider_id
  return default_user

# Store settings that might be reused
WELCOME_MESSAGE = """👋 Hi! I'm your networking assistant.
I can help you analyze network data using telemetry, including:
- Device information
- Interface status
- Routing tables
- Protocol states
- And more!

What would you like to know about your network?"""

@cl.on_chat_start
async def start():
    """Initialize the chat session with a welcome message."""
    # Generate and store thread ID
    cl.user_session.set("thread_id", generate_thread_id())
    
    # Send welcome message
    await cl.Message(content=WELCOME_MESSAGE).send()

@cl.on_chat_resume
async def on_chat_resume(thread: Dict):
    """Resume the chat session by restoring the thread_id."""
    # The 'thread' dictionary contains persisted data.
    # We need to extract the 'user_session' and then the 'thread_id'.
    
    # Debugging: Print the structure of the thread object
    # print(f"[DEBUG] Resuming chat, thread data: {json.dumps(thread, indent=2)}") 
    
    # Chainlit automatically restores messages/elements.
    # We need to manually restore the thread_id to the current session
    # so that subsequent calls to on_message use the correct thread.
    try:
        # Access the user_session dictionary within the thread object
        user_session_data = thread.get("user_session") 
        if user_session_data:
            thread_id = user_session_data.get("thread_id")
            if thread_id:
                cl.user_session.set("thread_id", thread_id)
                print(f"[DEBUG] Restored thread_id: {thread_id} to user session.")
            else:
                 print("[DEBUG] 'thread_id' not found in persisted user_session.")
                 # Handle case where thread_id is missing, maybe start a new one?
                 # cl.user_session.set("thread_id", generate_thread_id()) 
        else:
            print("[DEBUG] 'user_session' not found in thread object during resume.")
            # Handle case where user_session is missing
            # cl.user_session.set("thread_id", generate_thread_id())

    except Exception as e:
        print(f"[DEBUG] Error restoring thread_id during on_chat_resume: {e}")
        # Fallback or error handling, e.g., start a new thread
        # cl.user_session.set("thread_id", generate_thread_id())
        await cl.Message(content="Error resuming conversation. Starting a new one.").send()


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
        
        # Keep track of processed tool outputs to avoid duplicates
        processed_tool_outputs = set()

        async for chunk in react_graph.astream(msg_state, config):
            print(f"\n[DEBUG] Chunk details:")
            print(f"Chunk type: {type(chunk)}")
            print(f"[DEBUG] Full chunk content: {chunk}")

            # Handle tool outputs
            if isinstance(chunk, dict) and 'tools' in chunk:
                messages = chunk['tools'].get('messages', [])
                if messages:
                    for message in messages:
                        if message.content and message.content not in processed_tool_outputs:
                            tool_output = message.content
                            async with cl.Step(
                                name="Telemetry Response",
                                type="tool",
                                show_input=False,
                                language="json"
                            ) as step:
                                await step.stream_token(tool_output)
                            # Add the processed output to our set
                            processed_tool_outputs.add(tool_output)

            # Handle assistant responses after tool output
            elif isinstance(chunk, dict) and 'assistant' in chunk:
                messages = chunk['assistant'].get('messages', [])
                if messages and messages[0].content:
                    content = messages[0].content
                    # Create message object first
                    msg = cl.Message(content="")
                    await msg.send() # Send placeholder to get a message ID
                    # Stream character by character
                    for char in content:
                        await msg.stream_token(char)
                        await cl.sleep(0.005) # Adjusted sleep slightly
                    # Finalize the message content after streaming
                    await msg.update()

    except Exception as e:
        print(f"[DEBUG] Error occurred: {str(e)}")
        print(f"[DEBUG] Error type: {type(e)}")
        await cl.Message(
            content=f"❌ An error occurred: {str(e)}", 
            author="Error"
        ).send()
    finally:
        print("[DEBUG] Executing finally block")