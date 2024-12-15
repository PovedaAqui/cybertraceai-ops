import chainlit as cl
from app import react_graph, generate_thread_id
from langchain_core.messages import HumanMessage
from langchain.callbacks.tracers.langchain import wait_for_all_tracers

# Store settings that might be reused
WELCOME_MESSAGE = """👋 Hi! I'm your networking assistant.
I can help you check interface status, descriptions, routing tables, and more.

Please provide the device IP and your query."""

async def get_credentials():
    """Gets or prompts for username and password using Chainlit UI"""
    try:
        print("[DEBUG] Starting get_credentials")
        
        # Check if credentials exist in session
        cached_credentials = cl.user_session.get("credentials")
        if cached_credentials:
            print("[DEBUG] Using cached credentials")
            return cached_credentials["username"], cached_credentials["password"]
            
        print("[DEBUG] No cached credentials found, requesting new ones")
        
        # Ask for username
        print("[DEBUG] Requesting username")
        username_res = await cl.AskUserMessage(
            content="Please enter your username:",
            timeout=120,
            raise_on_timeout=True
        ).send()
        print(f"[DEBUG] Got username response: {username_res}")
        
        if not username_res:
            raise Exception("Username is required")
            
        # Try to remove username using message ID
        try:
            print(f"[DEBUG] Attempting to remove message with ID: {username_res['id']}")
            await cl.Message(
                id=username_res['id'],
                content=username_res['output']
            ).remove()
            print("[DEBUG] Successfully removed username message")
        except Exception as e:
            print(f"[DEBUG] Error removing username message: {str(e)}")

        # Ask for password
        print("[DEBUG] Requesting password")
        password_res = await cl.AskUserMessage(
            content="Please enter your password:",
            timeout=120,
            raise_on_timeout=True,
            type="password"
        ).send()
        print(f"[DEBUG] Got password response: {password_res}")

        if not password_res:
            raise Exception("Password is required")
            
        # Try to remove password using message ID
        try:
            print(f"[DEBUG] Attempting to remove message with ID: {password_res['id']}")
            await cl.Message(
                id=password_res['id'],
                content=password_res['output']
            ).remove()
            print("[DEBUG] Successfully removed password message")
        except Exception as e:
            print(f"[DEBUG] Error removing password message: {str(e)}")

        # Cache the credentials in session
        credentials = {
            "username": username_res['output'],
            "password": password_res['output']
        }
        cl.user_session.set("credentials", credentials)
        print("[DEBUG] Credentials cached in session")

        return credentials["username"], credentials["password"]

    except Exception as e:
        print(f"[DEBUG] Error in get_credentials: {str(e)}")
        print(f"[DEBUG] Error type: {type(e)}")
        raise Exception(f"Failed to get credentials: {str(e)}")

@cl.on_chat_start
async def start():
    """Initialize the chat session with a welcome message."""
    # Generate and store thread ID
    cl.user_session.set("thread_id", generate_thread_id())
    
    # Get credentials at start
    try:
        await get_credentials()
    except Exception as e:
        await cl.Message(content=f"Failed to get credentials: {str(e)}").send()
        return
    
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
                                name="Command Output",
                                type="tool",
                                show_input=False,
                                language="bash"
                            ) as step:
                                for line in tool_output.split('\n'):
                                    await step.stream_token(f"{line}\n")
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