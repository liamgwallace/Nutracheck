"""
Multi-provider AI agent configuration for browser automation.
Supports Claude (Anthropic), OpenAI, and Google Gemini.
"""

import os
from typing import List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm(provider: Optional[str] = None, model: Optional[str] = None):
    """
    Get a language model based on the provider.

    :param provider: AI provider ('claude', 'openai', or 'google'). Defaults to AI_PROVIDER env var or 'claude'
    :param model: Specific model to use. If not provided, uses sensible defaults
    :return: Configured LLM instance
    :raises: ValueError if provider is unknown or API key is missing
    """
    if provider is None:
        provider = os.getenv('AI_PROVIDER', 'claude').lower()

    if provider == 'claude':
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable must be set for Claude")

        model_name = model or "claude-3-5-sonnet-20241022"
        return ChatAnthropic(
            model=model_name,
            anthropic_api_key=api_key,
            temperature=0,
            max_tokens=4096
        )

    elif provider == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set for OpenAI")

        model_name = model or "gpt-4o"
        return ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            temperature=0
        )

    elif provider == 'google':
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable must be set for Google")

        model_name = model or "gemini-2.0-flash-exp"
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0
        )

    else:
        raise ValueError(f"Unknown AI provider: {provider}. Must be 'claude', 'openai', or 'google'")


def get_automation_prompt():
    """
    Get the system prompt template for browser automation.

    :return: PromptTemplate for the ReAct agent
    """
    template = """You are an AI assistant helping to automate web browser interactions on the Nutracheck website.

You are already logged in to Nutracheck and ready to help the user with their request.

Available tools:
{tools}

Tool names: {tool_names}

When using tools:
1. Always think step-by-step about what you need to do
2. Use navigate_to_url to go to different pages within Nutracheck
3. Use get_page_content to examine what's on the page
4. Use click_element, type_text for interactions
5. Use wait_for_element when pages are loading
6. Use execute_javascript for complex data extraction
7. Take screenshots if the user wants visual confirmation

Important guidelines:
- Stay within the Nutracheck domain (nutracheck.co.uk)
- Be precise with CSS selectors - examine the page content first if unsure
- If something doesn't work, try alternative approaches
- Provide clear summaries of what you found or did

User's request: {input}

Thought process:
{agent_scratchpad}"""

    return PromptTemplate(
        template=template,
        input_variables=["input", "tools", "tool_names", "agent_scratchpad"]
    )


def create_browser_agent(tools: List[BaseTool], provider: Optional[str] = None, model: Optional[str] = None) -> AgentExecutor:
    """
    Create a ReAct agent for browser automation.

    :param tools: List of LangChain tools (Selenium tools)
    :param provider: AI provider ('claude', 'openai', or 'google')
    :param model: Specific model to use
    :return: Configured AgentExecutor
    """
    llm = get_llm(provider, model)
    prompt = get_automation_prompt()

    # Create the ReAct agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=15,
        max_execution_time=300,  # 5 minute timeout
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )

    return agent_executor


def run_automation_task(tools: List[BaseTool], instructions: str, provider: Optional[str] = None) -> dict:
    """
    Run an automation task with the given instructions.

    :param tools: List of LangChain tools (Selenium tools)
    :param instructions: User's instructions for what to do
    :param provider: AI provider to use
    :return: Dictionary with 'output', 'success', and 'intermediate_steps'
    """
    try:
        agent_executor = create_browser_agent(tools, provider)

        result = agent_executor.invoke({
            "input": instructions
        })

        return {
            "output": result.get("output", ""),
            "success": True,
            "intermediate_steps": result.get("intermediate_steps", [])
        }

    except Exception as e:
        return {
            "output": f"Error running automation: {str(e)}",
            "success": False,
            "intermediate_steps": []
        }
