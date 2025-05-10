# CybertraceAI-Ops

CybertraceAI-Ops is an open-source AI agent designed to simplify IT network observability through natural language interactions.

## Overview

CybertraceAI-Ops uses large language models (LLMs) to interpret and analyze network telemetry data, making network management, troubleshooting, and monitoring, more accessible and efficient. It combines:
- Cloud-based AI Inference (Local AI Inference Available using Ollama or vLLM)
- Chainlit for interactive chat interface
- LangGraph for LLM orchestration
- SuzieQ for telemetry data analysis
- Tools selection using MCP server
- Local tool for timestamp humanization

## Installation

1. **Prerequisites**
   - Python 3.10 or higher
   - Git
   - **AI Inference Setup (Choose one or both):**
     - **Cloud-based AI Inference:** Access to an API service (e.g., OpenRouter, Groq, Cerebras, AWS, Azure). You will need to obtain an API key from your chosen provider and configure it as an environment variable (see Step 5).
     - **Local AI Inference (Optional):** For running models locally, have [Ollama](https://ollama.ai/) or vLLM installed and running. If using Ollama, ensure you have pulled the desired model (see Step 4).

2. **Clone the Repository**
   ```bash
   git clone https://github.com/povedaaqui/CybertraceAI-Ops.git
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
   This step is primarily for local inference using Ollama. If you are exclusively using cloud-based inference, you might not need to pull local models.
   ```bash
   ollama pull llama3.1:8b # Example for Ollama
   ```

5. **Configure Environment Variables**
   Create a `.env` file in the root directory of the project if it doesn't already exist. Add the following environment variables required for the application to function correctly:

   - **`MCP_SERVER_COMMAND_PATH`**: This variable is crucial for the agent to communicate with the MCP (Multi-Capability Protocol) server, which provides access to SuzieQ tools. Set it to the absolute path of the Python script that starts the MCP server.
     ```env
     MCP_SERVER_COMMAND_PATH=/path/to/your/mcp_server_script.py
     ```
     *Replace `/path/to/your/mcp_server_script.py` with the actual absolute path to the MCP server on your system*

   - **API Keys for Cloud Inference (If Applicable):** If you are using a cloud-based AI inference service, you will need to set the appropriate environment variable for your API key (e.g., `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, etc.).
     ```env
     # Example for OpenRouter
     OPENROUTER_API_KEY=your_openrouter_api_key_here
     OPENROUTER_BASE_URL=https://openrouter.ai/api/v1 # Or your specific provider's URL
     ```
     Refer to the `app.py` file and your AI service provider's documentation for the specific environment variable names and any additional required variables (like base URLs).

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
- Local execution using Ollama language models (optional)
- Zero-cloud dependency with Ollama - runs entirely on your infrastructure
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
- All your data is stored locally
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

Architectural Features:
- Real-time feedback via streaming responses
- Robust error handling and debugging capabilities
- Context-aware dynamic tool selection
- Session-based state management for conversational context
- Modular design for straightforward extensibility

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
- Tool selection based on context

We believe that combining suzieq's powerful observability engine with AI-driven natural language processing creates a more accessible and efficient way to understand your network.

## Contributing

We welcome contributions!

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](./LICENSE) file for more details.

## Support

- Create an issue on GitHub
- <!-- Join our [Discord community](https://discord.gg/#) -->
- Email: luis.poveda@cybertraceai.com