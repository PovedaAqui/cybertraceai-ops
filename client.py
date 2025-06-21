import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from os import getenv, path

# Load environment variables from .env file
load_dotenv()

mcp_server_path = getenv("MCP_SERVER_COMMAND_PATH")

mcp_server_cwd = None
if mcp_server_path and path.exists(mcp_server_path):
    mcp_server_cwd = path.dirname(mcp_server_path)

# Define the MCP server connection using MultiServerMCPClient
# We give our server a name, e.g., "suzieq_server", for the client to manage.
client = MultiServerMCPClient(
    {
        "suzieq_server": {
            "command": "uv",
            "args": [
                "run",
                "python",
                # IMPORTANT: Ensure this path is correct for your system
                mcp_server_path,
            ],
            "transport": "stdio",
            "cwd": mcp_server_cwd,
        }
    }
)

async def load_all_mcp_tools():
    """
    Loads all tools from all configured MCP servers using MultiServerMCPClient.
    The client handles session creation and teardown for the get_tools call.
    """
    print("[MCP INFO] Loading tools using MultiServerMCPClient...")
    try:
        # The get_tools() method handles connecting, loading tools, and disconnecting.
        loaded_tools = await client.get_tools()
        print(f"[MCP INFO] Loaded {len(loaded_tools)} MCP tools.")
        return loaded_tools
    except Exception as e:
        # Provide a more detailed error message for easier debugging.
        print(f"[MCP CRITICAL] Failed to load tools with MultiServerMCPClient: {e}")
        print("[MCP CRITICAL] Please check that the MCP_SERVER_COMMAND_PATH in your .env file is correct and the server is operational.")
        return []

# --- Load Tools on Module Import ---
# This block runs once when the module is first imported by another script.
tools = []
try:
    # asyncio.run() creates a new event loop to execute our async function.
    tools = asyncio.run(load_all_mcp_tools())

    if not tools:
        print("[MCP WARNING] No tools were loaded. Assistant will have limited capabilities.")

except Exception as e:
    # Catch any other unexpected errors during the setup process.
    print(f"[MCP CRITICAL] Unhandled exception during MCP setup: {e}")

# No atexit shutdown is explicitly needed here. `client.get_tools()` is designed
# to manage the lifecycle of the connection and the underlying subprocess for its
# single operation. If the server needed to be long-lived across multiple calls,
# a different pattern (like using `async with client.session(...)`) would be required.