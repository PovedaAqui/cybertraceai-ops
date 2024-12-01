from netmiko import ConnectHandler
from langchain.tools import StructuredTool
import chainlit as cl

async def get_credentials():
    """Prompts for username and password using Chainlit UI"""
    try:
        print("[DEBUG] Starting get_credentials")
        
        # Ask for username
        print("[DEBUG] Requesting username")
        username_res = await cl.AskUserMessage(
            content="Please enter your username:",
            timeout=120,
            raise_on_timeout=True
        ).send()
        print(f"[DEBUG] Got username response: {username_res}")
        print(f"[DEBUG] Username response type: {type(username_res)}")
        print(f"[DEBUG] Username response keys: {username_res.keys()}")

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
            content=" Please enter your password:",
            timeout=120,
            raise_on_timeout=True,
            type="password"
        ).send()
        print(f"[DEBUG] Got password response: {password_res}")
        print(f"[DEBUG] Password response type: {type(password_res)}")

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

        return username_res['output'], password_res['output']

    except Exception as e:
        print(f"[DEBUG] Error in get_credentials: {str(e)}")
        print(f"[DEBUG] Error type: {type(e)}")
        raise Exception(f"Failed to get credentials: {str(e)}")

async def show_interface_description(device_ip: str) -> str:
    """Executes 'show interface description' command on a Cisco device."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show interface description")
        return output 
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_ip_route_cisco(device_ip: str) -> str:
    """Executes 'show ip route' command on a Cisco device to display the routing table."""
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

async def show_ip_interface_brief(device_ip: str) -> str:
    """Executes 'show ip interface brief' command on a Cisco device to display interface status."""
    username, password = await get_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show ip interface brief")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

# Create structured tools from the functions
tools = [
    StructuredTool.from_function(
        show_interface_description,
        coroutine=show_interface_description,
        name="show_interface_description",
        description="Executes 'show interface description' command on a Cisco device."
    ),
    StructuredTool.from_function(
        show_ip_route_cisco,
        coroutine=show_ip_route_cisco,
        name="show_ip_route_cisco",
        description="Executes 'show ip route' command on a Cisco device."
    ),
    StructuredTool.from_function(
        show_ip_interface_brief,
        coroutine=show_ip_interface_brief,
        name="show_ip_interface_brief",
        description="Executes 'show ip interface brief' command on a Cisco device."
    )
] 