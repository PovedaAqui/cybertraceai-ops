# CybertraceAI

CybertraceAI is an open-source AI agent designed to simplify network management through natural language interactions. It currently specializes in Cisco networking devices, with plans to expand support to other vendors like SONiC and Juniper.

## Overview

CybertraceAI uses local language models to interpret and execute network commands, making network management more accessible and efficient. It combines:
- Ollama for local LLM processing (llama 3.2 3B) and embeddings (Nomic)
- Chainlit for interactive chat interface
- Langchain for LLM orchestration
- Netmiko for device communication
- Dynamic tool selection using embeddings

## Roadmap

CybertraceAI is being developed in phases, with each phase introducing new capabilities:

1. **Verification Module** (Currently in Development)
   - Support for common show commands
   - Real-time command interpretation
   - Basic network status monitoring
   - Device configuration validation

2. **Configuration Module** (Pending)
   - Support for configuration commands
   - Human-in-the-loop approval process
   - Configuration validation and rollback
   - Change management integration
   - Configuration templates and best practices

3. **Observability Module** (Pending)
   - Advanced telemetry collection
   - Performance metrics analysis
   - Custom monitoring dashboards
   - Anomaly detection
   - Historical data analysis

4. **Proactivity Module** (Pending)
   - Automated issue detection
   - Predictive maintenance
   - Network optimization recommendations
   - Automated remediation workflows
   - Capacity planning insights

## Features

- Natural language interface for network commands
- Local execution using Ollama language models (llama 3.2 3B)
- Dynamic tool selection using Nomic embeddings
- Zero-cloud dependency - runs entirely on your infrastructure
- Secure credential management with session-based storage
- Interactive streaming responses with interpretation
- Supports the following Cisco networking commands:
  - `show running-config` - View current device configuration
  - `show version` - Check system hardware and software status
  - `show ip route` - View IP routing table
  - `show interfaces` - Check detailed interface information
  - `show cdp neighbors` - View connected devices
  - `show vlan` - Check VLAN configuration
  - `show spanning-tree` - View spanning tree status
  - `show ip ospf` - Check OSPF routing information
  - `show ip bgp` - View BGP routing information
  - `show processes cpu` - Monitor CPU utilization
  - `show interface description` - View interface descriptions
  - `show ip interface brief` - Check interface IP and status
  - `show ip protocols` - View IP protocol information
  - `show logging` - View system logs and events

## Known Issues

- The `show running-config` and `show logging` commands may experience timeout issues with larger configurations.

## Prerequisites

- Python 3.11 or higher
- Ollama installed locally with:
  - llama 3.2 3B model for command processing
  - Nomic embedding model for tool selection
- Access to Cisco networking devices
- Required Python packages:
  - chainlit
  - langchain
  - netmiko
  - langgraph
- Minimum 16GB RAM required
- 64GB free disk space
- NVIDIA Series 40 graphics card is desirable for optimal performance

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cybertrace-ai.git
   cd cybertrace-ai
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   
   # Activate on Windows CMD
   .\venv\Scripts\activate.bat
   
   # Activate on Windows PowerShell
   .\venv\Scripts\Activate.ps1

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings if needed
   ```

5. Run CybertraceAI:
   ```bash
   chainlit run chainlit_app.py
   ```

## Usage

Once configured, you can start interacting with CybertraceAI using natural language commands. The system will securely prompt for device credentials on first use and cache them for the session.

### Example Commands:
```bash
# Check interface status
"Show me the status of all interfaces on 192.168.1.10"

# Verify VLAN configuration
"List all VLANs and their associated ports on 10.0.0.1"

# Troubleshoot connectivity
"Check if there are any errors on GigabitEthernet1/0/1 for device 172.16.0.100"

# View running configuration
"Show the running configuration of device 192.168.2.50"
```

## Extending Commands

CybertraceAI can be extended with additional Cisco IOS commands by modifying the following files:

1. In `tools.py`:
   ```python
   # Add to cisco_commands dictionary
   cisco_commands = {
       # ... existing commands ...
       "your new command": "Description of the command",
   }
   ```

2. The system will automatically:
   - Create the necessary tool functions
   - Register the tools with unique IDs
   - Index the commands in the vector store for dynamic selection

3. Update the command description in `app.py` system template under the appropriate category:
   ```python
   AVAILABLE TOOLS:
   // ... existing categories ...
   CATEGORY:
   - your_new_command: Description of what it does
   ```

Remember to:
- Ensure the command is supported by Cisco IOS
- Add proper error handling
- Test thoroughly before deployment
- Consider command timeout requirements

## Security Considerations

- Credentials are stored only in session memory
- Password inputs are masked in the UI
- No data is sent to external servers
- All processing happens locally
- Automatic credential cleanup
- Session-based authentication

## Architecture

- `chainlit_app.py`: Main application interface and chat handling
- `app.py`: Core logic and LLM configuration
- `tools.py`: Network command implementations
- Uses Langchain for LLM orchestration
- Implements streaming responses for real-time feedback
- Includes comprehensive error handling and debugging

## Contributing

We welcome contributions!

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](./LICENSE) file for more details.

## Support

- Create an issue on GitHub
- Join our [Discord community](https://discord.gg/#)
- Email: luis.poveda@cybertraceai.com

