"""
Custom Selenium tools for LangChain agents.
Provides browser automation capabilities for AI-powered navigation and data extraction.
"""

import base64
import time
from typing import Optional, Dict, Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SeleniumToolInput(BaseModel):
    """Base input schema for Selenium tools."""
    pass


class NavigateInput(BaseModel):
    """Input for navigate tool."""
    url: str = Field(description="The URL to navigate to")


class ClickInput(BaseModel):
    """Input for click tool."""
    selector: str = Field(description="CSS selector or XPath for the element to click")
    selector_type: str = Field(default="css", description="Type of selector: 'css' or 'xpath'")


class TypeTextInput(BaseModel):
    """Input for type_text tool."""
    selector: str = Field(description="CSS selector or XPath for the input element")
    text: str = Field(description="Text to type into the element")
    selector_type: str = Field(default="css", description="Type of selector: 'css' or 'xpath'")


class GetContentInput(BaseModel):
    """Input for get_content tool."""
    selector: Optional[str] = Field(default=None, description="Optional CSS selector to get content from specific element. If not provided, returns full page HTML")
    selector_type: str = Field(default="css", description="Type of selector: 'css' or 'xpath'")


class ScreenshotInput(BaseModel):
    """Input for screenshot tool."""
    full_page: bool = Field(default=True, description="Whether to capture full page or just viewport")


class WaitForInput(BaseModel):
    """Input for wait_for tool."""
    selector: str = Field(description="CSS selector or XPath for the element to wait for")
    selector_type: str = Field(default="css", description="Type of selector: 'css' or 'xpath'")
    timeout: int = Field(default=10, description="Timeout in seconds")


class ExecuteJSInput(BaseModel):
    """Input for execute_js tool."""
    script: str = Field(description="JavaScript code to execute")


class GetAttributeInput(BaseModel):
    """Input for get_attribute tool."""
    selector: str = Field(description="CSS selector or XPath for the element")
    attribute: str = Field(description="Attribute name to retrieve (e.g., 'href', 'value', 'class')")
    selector_type: str = Field(default="css", description="Type of selector: 'css' or 'xpath'")


class NavigateTool(BaseTool):
    """Navigate to a URL."""
    name: str = "navigate_to_url"
    description: str = "Navigate the browser to a specific URL. Use this to go to different pages."
    args_schema: type[BaseModel] = NavigateInput
    driver: Any = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, url: str) -> str:
        try:
            self.driver.get(url)
            time.sleep(1)  # Brief pause for page to start loading
            return f"Successfully navigated to {url}. Current URL: {self.driver.current_url}"
        except Exception as e:
            return f"Error navigating to {url}: {str(e)}"


class ClickTool(BaseTool):
    """Click an element on the page."""
    name: str = "click_element"
    description: str = "Click an element on the page using a CSS selector or XPath. Use this to click buttons, links, etc."
    args_schema: type[BaseModel] = ClickInput
    driver: Any = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, selector: str, selector_type: str = "css") -> str:
        try:
            by = By.CSS_SELECTOR if selector_type == "css" else By.XPATH
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by, selector))
            )
            element.click()
            return f"Successfully clicked element: {selector}"
        except TimeoutException:
            return f"Error: Element not found or not clickable: {selector}"
        except Exception as e:
            return f"Error clicking element {selector}: {str(e)}"


class TypeTextTool(BaseTool):
    """Type text into an input field."""
    name: str = "type_text"
    description: str = "Type text into an input field using a CSS selector or XPath. Use this to fill forms."
    args_schema: type[BaseModel] = TypeTextInput
    driver: Any = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, selector: str, text: str, selector_type: str = "css") -> str:
        try:
            by = By.CSS_SELECTOR if selector_type == "css" else By.XPATH
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, selector))
            )
            element.clear()
            element.send_keys(text)
            return f"Successfully typed text into element: {selector}"
        except Exception as e:
            return f"Error typing into element {selector}: {str(e)}"


class GetContentTool(BaseTool):
    """Get HTML content from the page."""
    name: str = "get_page_content"
    description: str = "Get HTML content from the page. Optionally specify a CSS selector to get content from a specific element, or leave empty to get the full page HTML."
    args_schema: type[BaseModel] = GetContentInput
    driver: Any = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, selector: Optional[str] = None, selector_type: str = "css") -> str:
        try:
            if selector:
                by = By.CSS_SELECTOR if selector_type == "css" else By.XPATH
                element = self.driver.find_element(by, selector)
                content = element.get_attribute('outerHTML')
                return f"Content from {selector}:\n{content[:2000]}"  # Limit to 2000 chars
            else:
                content = self.driver.page_source
                return f"Page HTML (first 2000 chars):\n{content[:2000]}"
        except Exception as e:
            return f"Error getting content: {str(e)}"


class ScreenshotTool(BaseTool):
    """Take a screenshot of the current page."""
    name: str = "take_screenshot"
    description: str = "Take a screenshot of the current page and return it as base64-encoded data."
    args_schema: type[BaseModel] = ScreenshotInput
    driver: Any = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, full_page: bool = True) -> str:
        try:
            screenshot_bytes = self.driver.get_screenshot_as_png()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            return f"Screenshot captured successfully (base64 length: {len(screenshot_base64)} chars)"
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"


class WaitForTool(BaseTool):
    """Wait for an element to appear on the page."""
    name: str = "wait_for_element"
    description: str = "Wait for an element to appear on the page using a CSS selector or XPath. Useful when waiting for dynamic content to load."
    args_schema: type[BaseModel] = WaitForInput
    driver: Any = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, selector: str, selector_type: str = "css", timeout: int = 10) -> str:
        try:
            by = By.CSS_SELECTOR if selector_type == "css" else By.XPATH
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return f"Element found: {selector}"
        except TimeoutException:
            return f"Timeout waiting for element: {selector}"
        except Exception as e:
            return f"Error waiting for element {selector}: {str(e)}"


class ExecuteJSTool(BaseTool):
    """Execute JavaScript code on the page."""
    name: str = "execute_javascript"
    description: str = "Execute JavaScript code in the browser context. Use this for custom interactions or data extraction that can't be done with other tools."
    args_schema: type[BaseModel] = ExecuteJSInput
    driver: Any = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, script: str) -> str:
        try:
            result = self.driver.execute_script(script)
            return f"JavaScript executed successfully. Result: {str(result)[:500]}"
        except Exception as e:
            return f"Error executing JavaScript: {str(e)}"


class GetAttributeTool(BaseTool):
    """Get an attribute value from an element."""
    name: str = "get_element_attribute"
    description: str = "Get an attribute value from an element (e.g., href, value, class). Use this to extract data from elements."
    args_schema: type[BaseModel] = GetAttributeInput
    driver: Any = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self, selector: str, attribute: str, selector_type: str = "css") -> str:
        try:
            by = By.CSS_SELECTOR if selector_type == "css" else By.XPATH
            element = self.driver.find_element(by, selector)
            value = element.get_attribute(attribute)
            return f"Attribute '{attribute}' value: {value}"
        except Exception as e:
            return f"Error getting attribute from {selector}: {str(e)}"


class GetCurrentURLTool(BaseTool):
    """Get the current URL."""
    name: str = "get_current_url"
    description: str = "Get the current URL of the browser."
    args_schema: type[BaseModel] = SeleniumToolInput
    driver: Any = Field(exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def _run(self) -> str:
        try:
            return f"Current URL: {self.driver.current_url}"
        except Exception as e:
            return f"Error getting current URL: {str(e)}"


def create_selenium_tools(driver):
    """
    Create all Selenium tools with the provided WebDriver instance.

    :param driver: Selenium WebDriver instance (already logged in to Nutracheck)
    :return: List of LangChain tools
    """
    return [
        NavigateTool(driver=driver),
        ClickTool(driver=driver),
        TypeTextTool(driver=driver),
        GetContentTool(driver=driver),
        ScreenshotTool(driver=driver),
        WaitForTool(driver=driver),
        ExecuteJSTool(driver=driver),
        GetAttributeTool(driver=driver),
        GetCurrentURLTool(driver=driver),
    ]
