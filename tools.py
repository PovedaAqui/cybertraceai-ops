import aiohttp
import json
from langchain.tools import StructuredTool
import uuid
from typing import Dict, Optional, Literal
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API configuration
BASE_URL = "http://localhost:8000/api/v2"
ACCESS_TOKEN = os.getenv('SUZIEQ_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    raise ValueError("SUZIEQ_ACCESS_TOKEN environment variable is not set")

# Define valid view values
ViewType = Literal["latest", "all", "changes"]
VerbType = Literal["show", "summarize"]

def create_api_call(resource: str, description: str) -> StructuredTool:
    """Creates a tool for executing Suzieq API calls."""
    # Create a safe name for the function
    safe_name = f"show_{resource.lower()}"
    
    async def api_command(
        view: ViewType = "latest",
        verb: VerbType = "show",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> str:
        """Execute Suzieq API call"""
        headers = {
            'accept': 'application/json',
            'access_token': ACCESS_TOKEN
        }
        
        # Build query parameters with fixed columns="default"
        params = {
            'view': view,
            'columns': 'default',  # Hardcoded to always use default
            'access_token': ACCESS_TOKEN
        }
        
        # Only add time parameters if they have actual values
        if start_time and start_time.lower() != 'null':
            params['start_time'] = start_time
        if end_time and end_time.lower() != 'null':
            params['end_time'] = end_time
            
        url = f"{BASE_URL}/{resource}/{verb}"
        
        try:
            async with aiohttp.ClientSession() as session:
                print(f"[DEBUG] Calling API: {url}")
                print(f"[DEBUG] Headers: {headers}")
                print(f"[DEBUG] Params: {params}")
                
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return f"Error: API returned status code {response.status}. Details: {error_text}"
                    
                    data = await response.json()
                    return json.dumps(data, indent=2)
                    
        except Exception as e:
            return f"Error calling API: {str(e)}"

    return StructuredTool.from_function(
        api_command,
        coroutine=api_command,
        name=safe_name,
        description=description
    )

# Define available Suzieq resources and their descriptions
suzieq_resources = {
    "device": "Shows information about network devices",
    "interface": "Shows detailed interface information",
    "route": "Shows routing table information",
    "bgp": "Shows BGP protocol information",
    "ospf": "Shows OSPF protocol information",
    "lldp": "Shows LLDP neighbor information",
    "vlan": "Shows VLAN information",
    "mac": "Shows MAC address table information",
    "arpnd": "Shows ARP/ND table information",
    "mlag": "Shows MLAG information",
    "evpnVni": "Shows EVPN VNI information",
    "fs": "Shows filesystem information",
    "sqpoller": "Shows poller information",
    "table": "Shows table information",
    "topology": "Shows network topology information (alpha)",
    "path": "Shows path information between endpoints"
}

# Create a tool registry with UUID keys
tool_registry: Dict[str, StructuredTool] = {
    str(uuid.uuid4()): create_api_call(resource, description)
    for resource, description in suzieq_resources.items()
}

# Create tools list from the registry
tools = list(tool_registry.values()) 