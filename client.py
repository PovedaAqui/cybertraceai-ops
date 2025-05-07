import asyncio
import atexit
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from dotenv import load_dotenv
from os import getenv

# Load environment variables from .env file
load_dotenv()

# Global store for MCP client and session (manage carefully in production)
mcp_session_store = {"session": None, "read": None, "write": None, "client": None}

server_params = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "python",
        # IMPORTANT: Ensure this path is correct for your system
        getenv("MCP_SERVER_COMMAND_PATH")
    ]
)

async def initialize_mcp_client_and_session(params):
    """Initializes and stores the MCP client and session."""
    print("[MCP DEBUG] Initializing MCP client and session...")
    try:
        # Create the client explicitly
        mcp_session_store["client"] = stdio_client(params)
        # Enter the client context to get read/write
        mcp_session_store["read"], mcp_session_store["write"] = await mcp_session_store["client"].__aenter__()
        # Create the session explicitly
        mcp_session_store["session"] = ClientSession(mcp_session_store["read"], mcp_session_store["write"])
        # Enter the session context
        await mcp_session_store["session"].__aenter__()
        # Initialize the session
        await mcp_session_store["session"].initialize()
        print("[MCP DEBUG] MCP session initialized and stored.")
    except Exception as e:
        print(f"[MCP ERROR] Failed to initialize MCP client/session: {e}")
        await shutdown_mcp_client() # Attempt cleanup on failure
        raise # Re-raise the exception

async def load_tools_from_session():
    """Loads tools using the stored MCP session."""
    if mcp_session_store["session"]:
        print("[MCP DEBUG] Loading tools using stored session...")
        try:
            load_tools = await load_mcp_tools(mcp_session_store["session"])
            print(f"[MCP DEBUG] Loaded {len(load_tools)} MCP tools")
            return load_tools
        except Exception as e:
            print(f"[MCP ERROR] Failed to load tools: {e}")
            return []
    else:
        print("[MCP ERROR] MCP session not initialized.")
        return []

async def shutdown_mcp_client():
    """Shuts down the stored MCP client and session."""
    print("[MCP DEBUG] Attempting to shut down MCP client and session...")
    session_closed = False
    if mcp_session_store["session"]:
        try:
            # Use try/except for __aexit__ as the resource might already be closed
            await mcp_session_store["session"].__aexit__(None, None, None)
            print("[MCP DEBUG] MCP session exited.")
            session_closed = True
        except Exception as e:
            print(f"[MCP ERROR] Error closing session (maybe already closed): {e}")
        finally:
             mcp_session_store["session"] = None

    client_closed = False
    if mcp_session_store["client"]:
        try:
             # Use try/except for __aexit__ as the resource might already be closed
            await mcp_session_store["client"].__aexit__(None, None, None)
            print("[MCP DEBUG] MCP client exited.")
            client_closed = True
        except Exception as e:
            print(f"[MCP ERROR] Error closing stdio client (maybe already closed): {e}")
        finally:
            mcp_session_store["client"] = None

    if session_closed and client_closed:
        print("[MCP DEBUG] MCP shutdown complete.")
    else:
        print("[MCP DEBUG] MCP shutdown finished (some resources might have failed to close cleanly).")

# --- Initialize MCP Client and Load Tools on module import ---
tools = [] # Initialize tools as an empty list
try:
    # Initialize MCP client/session globally first
    asyncio.run(initialize_mcp_client_and_session(server_params))

    # Load tools using the global session
    # Ensure tools are loaded only if initialization succeeded
    if mcp_session_store["session"]:
         tools = asyncio.run(load_tools_from_session())
    else:
         print("[MCP ERROR] Skipping tool loading due to failed initialization.")
         # tools remains []

    if not tools:
        print("[MCP WARNING] No tools were loaded. Assistant will have limited capabilities.")

except Exception as e:
    print(f"[MCP CRITICAL] Unhandled exception during MCP setup: {e}")
    # tools remains []

# Register the shutdown function to be called on exit
# Note: atexit may not work reliably for all termination signals or async cleanup.
# Consider more robust shutdown mechanisms for production applications (e.g., signal handlers).
atexit.register(lambda: asyncio.run(shutdown_mcp_client())) 