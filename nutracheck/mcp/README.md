# Nutracheck MCP Automation Service

AI-powered browser automation service for Nutracheck using the Model Context Protocol (MCP).

## Overview

This MCP service provides an AI agent that can automate browser interactions on the Nutracheck website. It automatically logs in to your Nutracheck account and then uses LangChain with Selenium to execute natural language instructions for:

- Extracting nutrition data
- Navigating the Nutracheck website
- Taking screenshots
- Filling forms
- Searching for specific information

## Architecture

```
User → MCP Client → MCP Server (exposes "automate_browser" tool)
                         ↓
                    LangChain Agent (Claude/OpenAI/Google)
                         ↓
              Custom Selenium Tools (navigate, click, extract, etc.)
                         ↓
                  Chrome Browser (pre-authenticated to Nutracheck)
```

## Features

- **Multi-Provider Support**: Use Claude (Anthropic), OpenAI GPT, or Google Gemini
- **Pre-Login**: Automatically logs in to Nutracheck before AI takes control
- **Browser Tools**: Navigate, click, type, extract content, take screenshots, execute JavaScript
- **Safe**: Browser stays within Nutracheck domain
- **Containerized**: Runs in Docker with headless Chrome

## Setup

### 1. Environment Variables

Set these in your `.env` file or docker-compose environment:

```bash
# Required
NUTRACHECK_EMAIL=your@email.com
NUTRACHECK_PASSWORD=your_password

# AI Provider (choose one: claude, openai, google)
AI_PROVIDER=claude

# API Key (set the one matching your AI_PROVIDER)
ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-proj-...
# GOOGLE_API_KEY=...
```

### 2. Docker Compose

The MCP service is defined in `docker-compose.yml`:

```bash
# Start the MCP service
docker-compose up nutracheck-mcp

# Or start all services
docker-compose up
```

### 3. Standalone Usage

You can also run the MCP server directly:

```bash
# Set environment variables
export NUTRACHECK_EMAIL=your@email.com
export NUTRACHECK_PASSWORD=your_password
export AI_PROVIDER=claude
export ANTHROPIC_API_KEY=sk-ant-...

# Run the server
python -m nutracheck.mcp.server
```

## MCP Tool

The service exposes one MCP tool:

### `automate_browser`

Automates browser interactions on Nutracheck using AI.

**Parameters:**
- `instructions` (required): Natural language instructions describing what to do
- `provider` (optional): AI provider to use (`claude`, `openai`, or `google`). Defaults to `AI_PROVIDER` env var

**Returns:**
- Text output from the AI agent
- Screenshot of the final page state

**Examples:**

```python
# Example 1: Get calorie data
{
  "instructions": "Navigate to my diary and get my total calories for the last 7 days"
}

# Example 2: Get weight history
{
  "instructions": "Go to my progress page and tell me my weight entries from January 2024"
}

# Example 3: Take a screenshot
{
  "instructions": "Navigate to the dashboard and take a screenshot"
}

# Example 4: Custom extraction
{
  "instructions": "Find my breakfast calories for yesterday and today"
}

# Example 5: Use different AI provider
{
  "instructions": "Get my latest weight measurement",
  "provider": "openai"
}
```

## Available Selenium Tools

The AI agent has access to these browser automation tools:

| Tool | Description |
|------|-------------|
| `navigate_to_url` | Navigate to a URL within Nutracheck |
| `click_element` | Click an element (button, link, etc.) |
| `type_text` | Type text into an input field |
| `get_page_content` | Extract HTML content from the page |
| `take_screenshot` | Capture a screenshot |
| `wait_for_element` | Wait for an element to appear |
| `execute_javascript` | Run custom JavaScript code |
| `get_element_attribute` | Get an attribute value from an element |
| `get_current_url` | Get the current page URL |

## Using with MCP Clients

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nutracheck": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file", "/path/to/.env",
        "ghcr.io/liamgwallace/nutracheck:latest"
      ],
      "env": {
        "MODE": "mcp"
      }
    }
  }
}
```

### Python MCP Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to the MCP server
server_params = StdioServerParameters(
    command="docker",
    args=[
        "run", "--rm", "-i",
        "--env-file", "/path/to/.env",
        "-e", "MODE=mcp",
        "ghcr.io/liamgwallace/nutracheck:latest"
    ]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # Call the automation tool
        result = await session.call_tool(
            "automate_browser",
            {
                "instructions": "Get my calorie intake for today"
            }
        )

        print(result)
```

## How It Works

1. **Server starts**: MCP server initializes and validates credentials
2. **Request received**: User sends instructions via MCP client
3. **Browser setup**: Chrome browser launches in headless mode
4. **Auto-login**: Server logs in to Nutracheck using stored credentials
5. **AI takes over**: LangChain agent receives instructions and authenticated browser
6. **Execution**: AI uses Selenium tools to complete the task
7. **Response**: Results and screenshot returned to user

## Troubleshooting

### Login fails

- Verify `NUTRACHECK_EMAIL` and `NUTRACHECK_PASSWORD` are correct
- Check if Nutracheck website structure has changed
- Look for errors in Docker logs: `docker logs nutracheck-mcp-automation`

### AI provider errors

- Verify the correct API key is set for your chosen provider
- Check API key has sufficient credits/quota
- Ensure `AI_PROVIDER` matches the API key you've set

### Browser errors

- Chrome may need updated selectors if Nutracheck UI changes
- Check Docker logs for ChromeDriver errors
- Ensure sufficient memory allocated to Docker

### Debugging

View logs in real-time:

```bash
docker logs -f nutracheck-mcp-automation
```

## Security Considerations

- **Credentials**: Stored only in environment variables, never logged
- **Browser**: Stays within Nutracheck domain, headless mode only
- **API Keys**: Keep secure, don't commit to version control
- **Network**: MCP uses stdio transport (no network exposure)

## Development

### Project Structure

```
nutracheck/mcp/
├── __init__.py           # Package initialization
├── server.py             # MCP server implementation
├── auth.py               # Nutracheck login logic
├── selenium_tools.py     # Custom Selenium tools for LangChain
├── ai_agents.py          # Multi-provider LangChain agent setup
└── README.md             # This file
```

### Adding New Tools

To add a new Selenium tool:

1. Create a new tool class in `selenium_tools.py`:

```python
class MyCustomTool(BaseTool):
    name: str = "my_tool"
    description: str = "What this tool does"
    args_schema: type[BaseModel] = MyToolInput
    driver: Any = Field(exclude=True)

    def _run(self, arg1: str) -> str:
        # Implementation
        pass
```

2. Add it to `create_selenium_tools()` function
3. Rebuild Docker image: `docker-compose build`

### Testing Locally

```bash
# Build the Docker image
docker build -f docker/Dockerfile -t nutracheck:dev .

# Run the MCP server
docker run --rm -i \
  -e MODE=mcp \
  -e NUTRACHECK_EMAIL=your@email.com \
  -e NUTRACHECK_PASSWORD=your_password \
  -e AI_PROVIDER=claude \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  nutracheck:dev
```

## License

Same as parent project.
