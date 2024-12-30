# CybertraceAI-Ops

CybertraceAI-Ops is an open-source AI agent designed to simplify network management through natural language interactions, focusing on network telemetry data analysis. It is one of the products offered by CybertraceAI.

## Overview

CybertraceAI-Ops uses local large language models (LLMs) to interpret and analyze network telemetry data, making network management more accessible and efficient. It combines:
- Ollama for local LLM processing (llama 3.1 8B) and embeddings (Nomic)
- Chainlit for interactive chat interface
- Langchain for LLM orchestration
- suzieq for telemetry data analysis
- Dynamic tool selection using embeddings

## Installation

1. **Prerequisites**
   - Python 3.9 or higher
   - [Ollama](https://ollama.ai/) installed and running
   - Git

2. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/CybertraceAI-Ops.git
   cd CybertraceAI-Ops
   ```

3. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Install and Pull Required Models**
   ```bash
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ```

## Running the Application

1. **Start Ollama**
   Ensure Ollama is running in the background

2. **Launch the Application**
   ```bash
   chainlit run chainlit_app.py --port 8010 -w
   ```
   The application will be available at `http://localhost:8010`

## Roadmap

CybertraceAI-Ops development focuses on the following priorities:

1. **Enhanced Functionalities**
   - Expanding telemetry data analysis capabilities
   - Adding more suzieq-based analysis tools
   - Improving data visualization options

2. **Integration with CybertraceAI-Live**
   - Seamless integration between telemetry and live data analysis
   - Unified interface for both products
   - Combined insights from historical and real-time data

## Features

- Natural language interface for network telemetry analysis
- Local execution using Ollama language models (llama 3.1 8B)
- Dynamic tool selection using Nomic embeddings
- Zero-cloud dependency - runs entirely on your infrastructure
- Secure API token management
- Interactive streaming responses with interpretation
- Powered by suzieq for comprehensive network telemetry analysis:
  - Device information and status
  - Interface analytics
  - Routing table analysis
  - BGP session monitoring
  - OSPF network state
  - LLDP neighbor discovery
  - VLAN configuration
  - MAC address tracking
  - ARP/ND table analysis
  - MLAG status
  - EVPN VNI information
  - Path analysis with EVPN overlay support
  - Network topology visualization
  - File system monitoring
  - Poller statistics

## Known Issues

- Assert functionality is currently under active development
- Some complex queries may require multiple interactions for optimal results
- Large dataset queries may experience longer processing times

## Special Thanks

Special thanks to Dinesh G Dutt, Justin Pietschand, and the entire suzieq team and contributors for creating the powerful network observability engine that powers CybertraceAI-Ops. Check out the suzieq project at [github.com/netenglabs/suzieq](https://github.com/netenglabs/suzieq).

## Security Considerations

- Secure API token management
- No data sent to external servers
- All processing happens locally
- Encrypted API communications

## Architecture

Core Components:
- `chainlit_app.py`: Interactive chat interface and streaming response handler
- `app.py`: Core logic, LLM orchestration, and tool selection
- `tools.py`: suzieq API integration and tool registry
- `embeddings.py`: Dynamic tool selection using vector embeddings

Integration Components:
- Langchain for LLM orchestration and tool management
- Chainlit for interactive chat interface
- suzieq for network telemetry analysis
- Ollama for local LLM processing
- Vector store for intelligent tool selection

Features:
- Streaming responses for real-time feedback
- Comprehensive error handling and debugging
- Dynamic tool selection based on query context
- Session-based state management
- Modular architecture for easy extension

## Philosophy

CybertraceAI-Ops shares suzieq's core philosophy about network observability. Like suzieq, we believe that:

- Network observability goes beyond traditional monitoring and alerting
- The true measure of observability is how easily you can answer questions about your network
- Network engineers and designers need tools that enhance their understanding of network behavior
- Multi-vendor support is essential for modern network environments
- Open-source solutions promote transparency and community-driven improvements

As the first open-source, multi-vendor network observability platform, suzieq established a foundation that CybertraceAI-Ops builds upon by adding:
- Natural language interaction with network telemetry data
- AI-powered interpretation of network states
- Dynamic tool selection based on context
- Interactive streaming responses for real-time insights

We believe that combining suzieq's powerful observability engine with AI-driven natural language processing creates a more accessible and efficient way to understand your network.

## Contributing

We welcome contributions!

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](./LICENSE) file for more details.

## Support

- Create an issue on GitHub
- Join our [Discord community](https://discord.gg/#)
- Email: luis.poveda@cybertraceai.com