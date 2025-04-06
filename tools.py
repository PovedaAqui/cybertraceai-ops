import aiohttp
import json
from langchain.tools import StructuredTool
import uuid
from typing import Dict, Optional, Literal, Any
from dotenv import load_dotenv
import os
import ast

# Load environment variables
load_dotenv()

# API configuration
BASE_URL = "http://192.168.0.47:8000/api/v2"
ACCESS_TOKEN = os.getenv('SUZIEQ_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    raise ValueError("SUZIEQ_ACCESS_TOKEN environment variable is not set")

# Define valid view values
ViewType = Literal["latest", "all", "changes"]
VerbType = Literal["show", "summarize", "assert"]

# Define available columns for each resource
AVAILABLE_COLUMNS = {
    "bgp": [
        "vrf", "peer", "peerHostname", "state", "asn", "peerAsn", "numChanges",
        "estdTime", "egressRmap", "ingressRmap", "keepaliveTime", "updateSource",
        "peerRouterId", "routerId", "bfdStatus", "peerIP"
    ],
    "interface": [
        "ifname", "state", "adminState", "type", "mtu", "vlan", "ipAddressList",
        "macaddr", "interfaceMac", "description", "portmode", "master"
    ],
    "device": [
        "model", "version", "vendor", "serialNumber", "status", "address",
        "bootupTimestamp", "architecture", "memory", "uptime"
    ],
    "lldp": [
        "ifname", "peerHostname", "peerIfname", "description", "mgmtIP",
        "peerMacaddr"
    ],
    "mac": [
        "vlan", "macaddr", "oif", "remoteVtepIp", "flags"
    ],
    "mlag": [
        "systemId", "state", "peerAddress", "role", "peerLink"
    ],
    "ospf": [
        "vrf", "ifname", "peerHostname", "area", "ifState", "nbrCount",
        "adjState", "peerIP", "numChanges", "lastChangeTime"
    ],
    "route": [
        "vrf", "prefix", "nexthopIps", "oifs", "protocol", "source",
        "preference", "ipvers", "action"
    ],
    "vlan": [
        "vlanName", "state", "interfaces", "vlan"
    ]
    # Other resources can be added here as needed
}

def create_api_call(resource: str, description: str) -> StructuredTool:
    """Creates a tool for executing Suzieq API calls."""
    safe_name = f"show_{resource.lower()}"
    
    async def api_command(
        verb: VerbType = "show",
        filters: Optional[Dict[str, Any] | str] = None
    ) -> str:
        """Execute Suzieq API call"""
        try:
            # Handle string filters and convert to dictionary
            if isinstance(filters, str):
                if filters.startswith('{') and filters.endswith('}'):
                    try:
                        filters = ast.literal_eval(filters)
                    except (ValueError, SyntaxError):
                        return "Error: Invalid filter format. Must be a dictionary"
                else:
                    filters = {"columns": filters.strip()}
            
            # Initialize filters dict if None
            filters = filters or {}
            
            # Ensure filters is a dictionary
            if not isinstance(filters, dict):
                return "Error: Filters must be a dictionary"
            
            # Handle list of columns if provided
            if "columns" in filters and isinstance(filters["columns"], list):
                columns = filters["columns"]
                # Remove the list from filters
                del filters["columns"]
                # Add each column separately
                for col in columns:
                    if isinstance(col, str):
                        if "columns" not in filters:
                            filters["columns"] = col
                        else:
                            # If columns already exists, append the new one
                            current = filters["columns"]
                            if isinstance(current, str):
                                filters["columns"] = f"{current},{col}"
            
            # Set default view if not provided
            if "view" not in filters:
                filters["view"] = "latest"
            
            # Validate view value
            if filters["view"] not in ["latest", "all", "changes"]:
                return "Error: 'view' must be one of: latest, all, changes"
                
            # Validate assert verb usage
            if verb == "assert" and resource.lower() not in ["bgp", "ospf", "interface"]:
                return "Error: 'assert' verb can only be used with BGP, OSPF, or Interface resources"
                
            headers = {
                'accept': 'application/json',
                'access_token': ACCESS_TOKEN
            }
            
            # Build base query parameters
            params = {
                'access_token': ACCESS_TOKEN
            }
            
            # Handle multiple columns by creating separate column parameters
            for key, value in filters.items():
                if key == "columns":
                    if isinstance(value, str):
                        # Split on comma or space if present
                        if "," in value or " " in value:
                            columns = [c.strip() for c in value.replace(",", " ").split()]
                            # Add each column as a separate parameter
                            for col in columns:
                                params[key] = col
                        else:
                            params[key] = value
                else:
                    params[key] = value
                
            url = f"{BASE_URL}/{resource}/{verb}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            return f"Error: API returned status code {response.status}. Details: {error_text}"
                        
                        data = await response.json()
                        return json.dumps(data, indent=2)
                        
            except Exception as e:
                return f"Error calling API: {str(e)}"
                
        except Exception as e:
            return f"Error processing request: {str(e)}"

    return StructuredTool.from_function(
        api_command,
        coroutine=api_command,
        name=safe_name,
        description=description
    )

# Update resource descriptions to include column information
common_filters = "Common filters: hostname, start-time, end-time, view (latest/all/changes), namespace. "

suzieq_resources = {
    "device": f"{common_filters}Network device inventory and status tracker. Hardware details, OS versions, uptime monitoring. Columns: {', '.join(AVAILABLE_COLUMNS['device'])}",
    
    "interface": f"{common_filters}Network interface configuration and status monitor. Tracks interface state, IPs, MTU, VLANs. Columns: {', '.join(AVAILABLE_COLUMNS['interface'])}",
    
    "route": f"{common_filters}Routing table analyzer. Shows network paths, next-hops, VRF configurations. Columns: {', '.join(AVAILABLE_COLUMNS['route'])}",
    
    "bgp": f"{common_filters}BGP protocol state monitor. Tracks BGP peers, ASNs, sessions. Supports assertion testing. Columns: {', '.join(AVAILABLE_COLUMNS['bgp'])}",
    
    "ospf": f"{common_filters}OSPF protocol state monitor. Shows neighbors, areas, interface states. Supports assertion testing. Columns: {', '.join(AVAILABLE_COLUMNS['ospf'])}",
    
    "lldp": f"{common_filters}LLDP neighbor discovery tracker. Maps physical connectivity and topology. Columns: {', '.join(AVAILABLE_COLUMNS['lldp'])}",
    
    "vlan": f"{common_filters}VLAN configuration tracker. Monitors VLAN states and interface assignments. Columns: {', '.join(AVAILABLE_COLUMNS['vlan'])}",
    
    "mac": f"{common_filters}MAC address table monitor. Tracks MAC locations and VTEP mappings. Columns: {', '.join(AVAILABLE_COLUMNS['mac'])}",
    
    "arpnd": f"{common_filters}ARP/ND table monitor. Maps IP addresses to MAC addresses.",
    
    "mlag": f"{common_filters}MLAG state tracker. Monitors multi-chassis link aggregation status. Columns: {', '.join(AVAILABLE_COLUMNS['mlag'])}",
    
    "evpnVni": f"{common_filters}EVPN VNI configuration monitor. Tracks EVPN and VTEP states.",
    
    "fs": f"{common_filters}Filesystem utilization tracker. Monitors storage states.",
    
    "sqpoller": f"{common_filters}Data collection monitor. Tracks polling status and timing.",
    
    "topology": f"{common_filters}Network topology analyzer. Maps network-wide connectivity.",
    
    "path": f"{common_filters}Network path tracer. Analyzes connectivity between endpoints."
}

# Create a tool registry with UUID keys
tool_registry: Dict[str, StructuredTool] = {
    str(uuid.uuid4()): create_api_call(resource, description)
    for resource, description in suzieq_resources.items()
}

# Create tools list from the registry
tools = list(tool_registry.values()) 