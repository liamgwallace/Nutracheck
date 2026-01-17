#!/usr/bin/env python3
"""
MCP server for AI-powered browser automation with Nutracheck.

This server exposes an MCP tool that accepts text instructions and uses
LangChain with Selenium to automate browser interactions on Nutracheck.
"""

import os
import sys
import json
import logging
import base64
import asyncio
from typing import Any, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from nutracheck.mcp.auth import create_chrome_driver, login_to_nutracheck, get_credentials_from_env
from nutracheck.mcp.selenium_tools import create_selenium_tools
from nutracheck.mcp.ai_agents import run_automation_task

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Global driver instance (reused across requests)
_driver = None
_driver_logged_in = False


def get_or_create_driver():
    """
    Get or create the global Chrome driver instance.
    Creates it on first call, reuses it on subsequent calls.

    :return: Selenium WebDriver instance
    """
    global _driver, _driver_logged_in

    if _driver is None:
        logger.info("Creating new Chrome driver...")
        _driver = create_chrome_driver(headless=True)
        _driver_logged_in = False
        logger.info("Chrome driver created successfully")

    return _driver


def ensure_logged_in(driver):
    """
    Ensure the driver is logged in to Nutracheck.
    Performs login if not already logged in.

    :param driver: Selenium WebDriver instance
    :return: True if logged in, False otherwise
    """
    global _driver_logged_in

    if _driver_logged_in:
        logger.info("Already logged in, skipping login")
        return True

    try:
        logger.info("Performing Nutracheck login...")
        username, password = get_credentials_from_env()
        login_to_nutracheck(driver, username, password)
        _driver_logged_in = True
        logger.info("Login successful")
        return True

    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False


def cleanup_driver():
    """Clean up the global driver instance."""
    global _driver, _driver_logged_in

    if _driver is not None:
        try:
            _driver.quit()
            logger.info("Driver cleaned up successfully")
        except:
            pass
        finally:
            _driver = None
            _driver_logged_in = False


async def handle_automation_request(instructions: str, provider: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle an automation request.

    :param instructions: User's instructions for what to automate
    :param provider: AI provider to use (claude, openai, google)
    :return: Dictionary with result, screenshot, and success status
    """
    driver = None
    try:
        # Get or create driver
        driver = get_or_create_driver()

        # Ensure we're logged in
        if not ensure_logged_in(driver):
            return {
                "success": False,
                "error": "Failed to log in to Nutracheck",
                "output": "",
                "screenshot": None
            }

        # Create Selenium tools
        logger.info("Creating Selenium tools...")
        tools = create_selenium_tools(driver)

        # Run the automation task
        logger.info(f"Running automation task with provider: {provider or 'default'}")
        logger.info(f"Instructions: {instructions}")

        result = run_automation_task(tools, instructions, provider)

        # Take a final screenshot
        screenshot_base64 = None
        try:
            screenshot_bytes = driver.get_screenshot_as_png()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        except Exception as e:
            logger.warning(f"Failed to capture screenshot: {e}")

        return {
            "success": result["success"],
            "output": result["output"],
            "screenshot": screenshot_base64,
            "error": None if result["success"] else result["output"]
        }

    except Exception as e:
        logger.error(f"Automation request failed: {e}", exc_info=True)

        # Try to capture error screenshot
        screenshot_base64 = None
        if driver:
            try:
                screenshot_bytes = driver.get_screenshot_as_png()
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            except:
                pass

        return {
            "success": False,
            "error": str(e),
            "output": "",
            "screenshot": screenshot_base64
        }


# Create MCP server
app = Server("nutracheck-automation")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="automate_browser",
            description=(
                "Automate browser interactions on Nutracheck using AI. "
                "Provide text instructions describing what you want to do, and the AI will "
                "navigate the Nutracheck website, extract data, fill forms, take screenshots, etc. "
                "The browser is automatically logged in to Nutracheck before the AI takes control. "
                "Examples: 'Get my calorie intake for the last 7 days', 'Navigate to my progress page and take a screenshot', "
                "'Find my weight entries from January 2024'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "instructions": {
                        "type": "string",
                        "description": "Natural language instructions describing what you want the AI to do on Nutracheck"
                    },
                    "provider": {
                        "type": "string",
                        "description": "AI provider to use: 'claude', 'openai', or 'google'. Defaults to AI_PROVIDER env var or 'claude'",
                        "enum": ["claude", "openai", "google"]
                    }
                },
                "required": ["instructions"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    if name != "automate_browser":
        raise ValueError(f"Unknown tool: {name}")

    instructions = arguments.get("instructions")
    provider = arguments.get("provider")

    if not instructions:
        raise ValueError("Missing required argument: instructions")

    # Run the automation
    result = await handle_automation_request(instructions, provider)

    # Prepare response
    response_parts = []

    # Add text output
    if result["success"]:
        output_text = f"✓ Automation completed successfully\n\n{result['output']}"
    else:
        output_text = f"✗ Automation failed\n\nError: {result['error']}\n\nOutput: {result['output']}"

    response_parts.append(TextContent(
        type="text",
        text=output_text
    ))

    # Add screenshot if available
    if result["screenshot"]:
        response_parts.append(ImageContent(
            type="image",
            data=result["screenshot"],
            mimeType="image/png"
        ))

    return response_parts


async def main():
    """Main entry point for the MCP server."""
    logger.info("=" * 60)
    logger.info("Starting Nutracheck MCP Automation Server")
    logger.info("=" * 60)

    # Verify credentials
    try:
        username, password = get_credentials_from_env()
        logger.info(f"Credentials loaded: {username[:3]}...@{username.split('@')[1]}")
    except Exception as e:
        logger.error(f"Failed to load credentials: {e}")
        sys.exit(1)

    # Verify AI provider configuration
    provider = os.getenv('AI_PROVIDER', 'claude').lower()
    logger.info(f"AI Provider: {provider}")

    if provider == 'claude':
        if not os.getenv('ANTHROPIC_API_KEY'):
            logger.error("ANTHROPIC_API_KEY not set")
            sys.exit(1)
    elif provider == 'openai':
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("OPENAI_API_KEY not set")
            sys.exit(1)
    elif provider == 'google':
        if not os.getenv('GOOGLE_API_KEY'):
            logger.error("GOOGLE_API_KEY not set")
            sys.exit(1)

    logger.info("Configuration validated successfully")
    logger.info("Server ready to accept requests")
    logger.info("=" * 60)

    try:
        # Run the MCP server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    finally:
        logger.info("Shutting down server...")
        cleanup_driver()
        logger.info("Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        cleanup_driver()
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)
        cleanup_driver()
        sys.exit(1)
