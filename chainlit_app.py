import chainlit as cl
from app import react_graph, generate_thread_id
from langchain_core.messages import HumanMessage
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
import asyncio

# Store settings that might be reused
WELCOME_MESSAGE = """👋 Hi! I'm your networking assistant.
I can help you check interface status, descriptions, routing tables, and more.

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
        
        msg = cl.Message(content="")
        already_streamed_content = set()  # Track what we've already sent
        tool_output_sent = False  # Flag to track if tool output has been sent
        current_buffer = ""  # Buffer for accumulating tokens
        
        async for chunk in react_graph.astream(msg_state, config):
            print(f"\n[DEBUG] Chunk details:")
            print(f"Chunk type: {type(chunk)}")
            print(f"[DEBUG] Full chunk content: {chunk}")
            
            # Extract content based on the chunk structure
            if isinstance(chunk, dict):
                if 'tools' in chunk and not tool_output_sent:
                    messages = chunk['tools'].get('messages', [])
                    if messages and messages[0].content:
                        content = f"```\n{messages[0].content}\n```"
                        # Stream tool output line by line
                        for line in content.split('\n'):
                            await msg.stream_token(line + '\n')
                        tool_output_sent = True
                elif 'assistant' in chunk:
                    messages = chunk['assistant'].get('messages', [])
                    if messages and messages[0].content:
                        assistant_content = messages[0].content
                        # Stream all content token by token, regardless of "Interpretation:"
                        if not '```' in assistant_content and assistant_content.strip():
                            for token in assistant_content.split():
                                await msg.stream_token(token + ' ')
                                await asyncio.sleep(0.01)  # Add small delay between tokens
        
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
        wait_for_all_tracers()