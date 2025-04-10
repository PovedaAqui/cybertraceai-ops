# CybertraceAI-Ops

CybertraceAI-Ops is an open-source AI agent designed to simplify network observability through natural language interactions. It is one of the products offered by CybertraceAI.

## Overview

CybertraceAI-Ops uses local large language models (LLMs) to interpret and analyze network telemetry data, making network management more accessible and efficient. It combines:
- Ollama for local LLM processing (llama 3.1 8B) and embeddings (Nomic)
- Chainlit for interactive chat interface
- Langchain for LLM orchestration
- suzieq for telemetry data analysis
- Dynamic tool selection using MCP server

## Installation

1. **Prerequisites**
   - Python 3.10 or higher
   - [Ollama](https://ollama.ai/) installed and running
   - Git

2. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/CybertraceAI-Ops.git
   cd CybertraceAI-Ops
   ```

3. **Set Up Virtual Environment and Install Dependencies**

   ### Using uv (Fast Python Package Installer)
   
   [uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.
   
   ```bash
   # Install uv if you don't have it yet
   pip install uv
   
   # Create a virtual environment
   uv venv .venv-uv
   
   # Activate the virtual environment
   # On Windows:
   .venv-uv\Scripts\activate
   # On Unix/MacOS:
   source .venv-uv/bin/activate
   
   # Install project and dependencies
   uv pip install -e .
   ```

   ### Using pip (Alternative Method)
   
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -e .
   ```

4. **Install and Pull Required Models**
   ```bash
   ollama pull llama3.1:8b
   ```

## Running the Application

1. **Start Ollama**
   Ensure Ollama is running in the background

2. **Launch the Application**
   ```bash
   chainlit run chainlit_app.py --port 8010 -w
   ```
   The application will be available at `http://localhost:8010`

## Enabling Chat History Persistence (Optional)

To persist chat history and user interactions, you can configure Chainlit's datalayer with a PostgreSQL database. This allows you to store conversation threads, user information, steps, elements, and feedback.

1.  **Deploy a PostgreSQL Database:**
    Set up a PostgreSQL instance. You can run one locally using Docker or use a managed cloud service.

2.  **Configure Environment Variable:**
    Add the database connection string to your environment file (e.g., `.env`). Chainlit will automatically detect and use it.
    ```env
    DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database_name>
    ```
    For example:
    ```env
    DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/chathistory
    ```

3.  **Apply Database Schema:**
    You'll need `prisma` installed (`npm install -g prisma` or use `npx`). Run the following command to apply the necessary database schema. This requires the `prisma/schema.prisma` file from the Chainlit datalayer setup. If you don't have it, you might need to clone or integrate parts of the [Chainlit datalayer repository](https://github.com/Chainlit/chainlit-datalayer).
    ```bash
    npx prisma migrate deploy
    ```

4.  **View Data (Optional):**
    To inspect the data stored in your database, you can use Prisma Studio:
    ```bash
    npx prisma studio
    ```

5.  **Enable Authentication:**
    Remember to configure user authentication in Chainlit to associate chat history with specific users. See the [Chainlit Authentication Docs](https://docs.chainlit.io/authentication/overview).

For more detailed information and advanced configurations (like cloud storage for elements), refer to the [Chainlit Datalayer repository](https://github.com/Chainlit/chainlit-datalayer).

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
- `client.py`: Handle MCP session

Integration Components:
- Langchain for LLM orchestration and tool management
- Chainlit for interactive chat interface
- suzieq for network telemetry analysis
- Ollama for local LLM processing

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