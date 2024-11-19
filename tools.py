from netmiko import ConnectHandler
from langchain.tools import StructuredTool

def show_interface_description(device_ip: str, username: str, password: str) -> str:
    """Executes 'show interface description' command on a Cisco device."""
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

def show_ip_route_cisco(device_ip: str, username: str, password: str) -> str:
    """Executes 'show ip route' command on a Cisco device to display the routing table."""
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

def show_ip_interface_brief(device_ip: str, username: str, password: str) -> str:
    """Executes 'show ip interface brief' command on a Cisco device to display interface status."""
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
    StructuredTool.from_function(show_interface_description),
    StructuredTool.from_function(show_ip_route_cisco),
    StructuredTool.from_function(show_ip_interface_brief)
] 