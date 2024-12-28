import chainlit as cl
from app import react_graph, generate_thread_id
from langchain_core.messages import HumanMessage
from langchain.callbacks.tracers.langchain import wait_for_all_tracers

# Store settings that might be reused
WELCOME_MESSAGE = """👋 Hi! I'm your networking assistant.
I can help you analyze network data using telemetry, including:
- Device information
- Interface status
- Routing tables
- Protocol states
And more!

What would you like to know about your network?"""

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
                    # Create message after tool output
                    msg = cl.Message(content="")
                    await msg.send()
                    # Stream character by character with faster speed
                    for char in content:
                        await msg.stream_token(char)
                        await cl.sleep(0.001)  # Reduced to 0.001 for smoother streaming
                    # Finalize the message
                    await msg.send()

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