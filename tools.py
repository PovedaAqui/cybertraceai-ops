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
BASE_URL = "http://localhost:8000/api/v2"
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
            
            # Handle multiple column filters
            columns = []
            for key, value in filters.items():
                if key == "columns":
                    columns.append(value)
                else:
                    params[key] = value
            
            # If we have columns, join them with commas for the API
            if columns:
                params["columns"] = ",".join(columns)
                
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
common_filters = "Common filters: hostname, start-time, end-time, view (latest/all/changes), namespace, columns."

suzieq_resources = {
    "device": f"{common_filters}Shows information about network devices. Use for: device inventory, hardware details, OS versions, uptime, and operational status. Available columns: {', '.join(AVAILABLE_COLUMNS['device'])}",
    
    "interface": f"{common_filters}Shows network interface details. Use for: interface status, configuration, IP addresses, MTU, VLANs, and link state. Available columns: {', '.join(AVAILABLE_COLUMNS['interface'])}",
    
    "route": f"{common_filters}Shows routing table information. Use for: network routes, next-hops, VRF paths, and route sources. Available columns: {', '.join(AVAILABLE_COLUMNS['route'])}",
    
    "bgp": f"{common_filters}Shows BGP protocol information. Use for: BGP neighbor status, ASN details, session state, and peer relationships. Supports 'assert' for troubleshooting. Available columns: {', '.join(AVAILABLE_COLUMNS['bgp'])}",
    
    "ospf": f"{common_filters}Shows OSPF protocol information. Use for: OSPF neighbor status, area configuration, interface state, and neighbor counts. Supports 'assert' for troubleshooting. Available columns: {', '.join(AVAILABLE_COLUMNS['ospf'])}",
    
    "lldp": f"{common_filters}Shows LLDP neighbor discovery information. Use for: physical connectivity, neighbor details, and topology mapping. Available columns: {', '.join(AVAILABLE_COLUMNS['lldp'])}",
    
    "vlan": f"{common_filters}Shows VLAN configuration and status. Use for: VLAN assignments, interface memberships, and VLAN state. Available columns: {', '.join(AVAILABLE_COLUMNS['vlan'])}",
    
    "mac": f"{common_filters}Shows MAC address table information. Use for: MAC address lookups, VTEP associations, and interface mappings. Available columns: {', '.join(AVAILABLE_COLUMNS['mac'])}",
    
    "arpnd": f"{common_filters}Shows ARP/ND table information. Use for: IP-to-MAC mappings, neighbor discovery, and address resolution",
    
    "mlag": f"{common_filters}Shows Multi-Chassis Link Aggregation information. Use for: MLAG status, peer relationships, and link state. Available columns: {', '.join(AVAILABLE_COLUMNS['mlag'])}",
    
    "evpnVni": f"{common_filters}Shows EVPN VNI information. Use for: EVPN configuration, VNI status, and VTEP details",
    
    "fs": f"{common_filters}Shows filesystem information. Use for: storage utilization and filesystem status",
    
    "sqpoller": f"{common_filters}Shows poller information. Use for: monitoring data collection status and timing",
    
    "topology": f"{common_filters}Shows network topology information. Use for: network-wide connectivity and path analysis",
    
    "path": f"{common_filters}Shows path information between endpoints. Use for: tracing network paths and analyzing connectivity"
}

# Create a tool registry with UUID keys
tool_registry: Dict[str, StructuredTool] = {
    str(uuid.uuid4()): create_api_call(resource, description)
    for resource, description in suzieq_resources.items()
}

# Create tools list from the registry
tools = list(tool_registry.values()) 