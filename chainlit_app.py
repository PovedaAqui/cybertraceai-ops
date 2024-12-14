import chainlit as cl
from app import react_graph, generate_thread_id
from langchain_core.messages import HumanMessage
from langchain.callbacks.tracers.langchain import wait_for_all_tracers

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
        tool_output_sent = False  # Flag to track if tool output has been sent

        async for chunk in react_graph.astream(msg_state, config):
            print(f"\n[DEBUG] Chunk details:")
            print(f"Chunk type: {type(chunk)}")
            print(f"[DEBUG] Full chunk content: {chunk}")

            # Handle tool outputs
            if isinstance(chunk, dict) and 'tools' in chunk and not tool_output_sent:
                messages = chunk['tools'].get('messages', [])
                if messages and messages[0].content:
                    tool_output = messages[0].content
                    
                    # Create a step for tool output with hidden input
                    async with cl.Step(
                        name="Command Output",
                        type="tool",
                        show_input=False,
                        language="bash"
                    ) as step:
                        for line in tool_output.split('\n'):
                            await step.stream_token(f"{line}\n")
                tool_output_sent = True

            # Handle assistant responses
            elif isinstance(chunk, dict) and 'assistant' in chunk:
                messages = chunk['assistant'].get('messages', [])
                if messages and messages[0].content:
                    assistant_content = messages[0].content
                    await msg.stream_token("\n")
                    for line in assistant_content.split('. '):
                        await msg.stream_token(f"{line.strip()}\n\n")

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