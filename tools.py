from netmiko import ConnectHandler
from langchain.tools import StructuredTool
import chainlit as cl
import re
import uuid
from typing import Dict

async def get_cached_credentials():
    """Gets cached credentials from the session"""
    credentials = cl.user_session.get("credentials")
    if not credentials:
        raise Exception("No credentials found in session")
    return credentials["username"], credentials["password"]

def create_cisco_tool(command: str, description: str) -> StructuredTool:
    """Creates a tool for executing a Cisco command."""
    # Create a safe name for the function
    safe_name = re.sub(r"[^\w\s]", "", command).replace(" ", "_").lower()
    
    async def cisco_command(device_ip: str) -> str:
        username, password = await get_cached_credentials()
        cisco_device = {
            'device_type': 'cisco_ios',
            'ip': device_ip,
            'username': username,
            'password': password,
        }
        try:
            with ConnectHandler(**cisco_device) as net_connect:
                output = net_connect.send_command(command, read_timeout=90)
            return output
        except Exception as e:
            return f"Error connecting to device: {str(e)}"

    return StructuredTool.from_function(
        cisco_command,
        coroutine=cisco_command,
        name=safe_name,
        description=description
    )

# Define available Cisco commands and their descriptions
cisco_commands = {
    "show running-config": "Shows the current running configuration of the device.",
    "show version": "Shows system hardware and software status.",
    "show ip route": "Shows the IP routing table.",
    "show interfaces": "Shows detailed interface information.",
    "show cdp neighbors": "Shows CDP neighbor information.",
    "show vlan": "Shows VLAN information.",
    "show spanning-tree": "Shows spanning tree information.",
    "show ip ospf": "Shows OSPF information.",
    "show ip bgp": "Shows BGP information.",
    "show processes cpu": "Shows CPU utilization.",
    "show interface description": "Shows interface descriptions.",
    "show ip interface brief": "Shows brief status of interfaces.",
    "show ip protocols": "Shows IP protocol information.",
    "show logging": "Shows the logging information from the device."
}

# Create a tool registry with UUID keys
tool_registry: Dict[str, StructuredTool] = {
    str(uuid.uuid4()): create_cisco_tool(command, description)
    for command, description in cisco_commands.items()
}

# Create tools list from the registry
tools = list(tool_registry.values()) 