from netmiko import ConnectHandler
from langchain.tools import StructuredTool
import chainlit as cl

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

async def show_running_config(device_ip: str) -> str:
    """Shows the current running configuration of the device."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show running-config")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_version(device_ip: str) -> str:
    """Shows system hardware and software status."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show version")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_ip_route(device_ip: str) -> str:
    """Shows the IP routing table."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show ip route")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_interfaces(device_ip: str) -> str:
    """Shows detailed interface information."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show interfaces")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_cdp_neighbors(device_ip: str) -> str:
    """Shows CDP neighbor information."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show cdp neighbors")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_vlan(device_ip: str) -> str:
    """Shows VLAN information."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show vlan")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_spanning_tree(device_ip: str) -> str:
    """Shows spanning tree information."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show spanning-tree")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_ip_ospf(device_ip: str) -> str:
    """Shows OSPF information."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show ip ospf")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_ip_bgp(device_ip: str) -> str:
    """Shows BGP information."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show ip bgp")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_processes_cpu(device_ip: str) -> str:
    """Shows CPU utilization."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show processes cpu")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

# Update the tools list
tools = [
    StructuredTool.from_function(
        show_running_config,
        coroutine=show_running_config,
        name="show_running_config",
        description="Shows the current running configuration of the device."
    ),
    StructuredTool.from_function(
        show_version,
        coroutine=show_version,
        name="show_version",
        description="Shows system hardware and software status."
    ),
    StructuredTool.from_function(
        show_ip_route,
        coroutine=show_ip_route,
        name="show_ip_route",
        description="Shows the IP routing table."
    ),
    StructuredTool.from_function(
        show_interfaces,
        coroutine=show_interfaces,
        name="show_interfaces",
        description="Shows detailed interface information."
    ),
    StructuredTool.from_function(
        show_cdp_neighbors,
        coroutine=show_cdp_neighbors,
        name="show_cdp_neighbors",
        description="Shows CDP neighbor information."
    ),
    StructuredTool.from_function(
        show_vlan,
        coroutine=show_vlan,
        name="show_vlan",
        description="Shows VLAN information."
    ),
    StructuredTool.from_function(
        show_spanning_tree,
        coroutine=show_spanning_tree,
        name="show_spanning_tree",
        description="Shows spanning tree information."
    ),
    StructuredTool.from_function(
        show_ip_ospf,
        coroutine=show_ip_ospf,
        name="show_ip_ospf",
        description="Shows OSPF information."
    ),
    StructuredTool.from_function(
        show_ip_bgp,
        coroutine=show_ip_bgp,
        name="show_ip_bgp",
        description="Shows BGP information."
    ),
    StructuredTool.from_function(
        show_processes_cpu,
        coroutine=show_processes_cpu,
        name="show_processes_cpu",
        description="Shows CPU utilization."
    )
] 