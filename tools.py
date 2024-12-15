from netmiko import ConnectHandler
from langchain.tools import StructuredTool
import chainlit as cl

async def get_cached_credentials():
    """Gets cached credentials from the session"""
    credentials = cl.user_session.get("credentials")
    if not credentials:
        raise Exception("No credentials found in session")
    return credentials["username"], credentials["password"]

async def show_running_config(device_ip: str) -> str:
    """Executes the 'show running-config' command on a Cisco device to display the current configuration."""
    username, password = await get_cached_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show running-config", read_timeout=90)
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_version(device_ip: str) -> str:
    """Shows system hardware and software status."""
    username, password = await get_cached_credentials()
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
    username, password = await get_cached_credentials()
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
    username, password = await get_cached_credentials()
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
    username, password = await get_cached_credentials()
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
    username, password = await get_cached_credentials()
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
    username, password = await get_cached_credentials()
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
    username, password = await get_cached_credentials()
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
    username, password = await get_cached_credentials()
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
    username, password = await get_cached_credentials()
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

async def show_interface_description(device_ip: str) -> str:
    """Shows interface descriptions."""
    username, password = await get_cached_credentials()
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

async def show_ip_interface_brief(device_ip: str) -> str:
    """Shows brief status of interfaces."""
    username, password = await get_cached_credentials()
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

async def show_ip_protocols(device_ip: str) -> str:
    """Shows IP protocol information."""
    username, password = await get_cached_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show ip protocols")
        return output
    except Exception as e:
        return f"Error connecting to device: {str(e)}"

async def show_logging(device_ip: str) -> str:
    """Shows the logging information from the device."""
    username, password = await get_cached_credentials()
    cisco_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
    }
    try:
        with ConnectHandler(**cisco_device) as net_connect:
            output = net_connect.send_command("show logging", read_timeout=90)
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
    ),
    StructuredTool.from_function(
        show_interface_description,
        coroutine=show_interface_description,
        name="show_interface_description",
        description="Shows interface descriptions."
    ),
    StructuredTool.from_function(
        show_ip_interface_brief,
        coroutine=show_ip_interface_brief,
        name="show_ip_interface_brief",
        description="Shows brief status of interfaces."
    ),
    StructuredTool.from_function(
        show_ip_protocols,
        coroutine=show_ip_protocols,
        name="show_ip_protocols",
        description="Shows IP protocol information."
    ),
    StructuredTool.from_function(
        show_logging,
        coroutine=show_logging,
        name="show_logging",
        description="Shows the logging information from the device."
    )
] 