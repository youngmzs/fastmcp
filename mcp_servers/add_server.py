# server.py
import httpx
from fastmcp import FastMCP
from pydantic import BaseModel
from fastmcp.prompts import Message,UserMessage, AssistantMessage
from fastmcp import Context, FastMCP

# Create an MCP server
mcp = FastMCP("Demo",port = 9999)

# ----------------------- tools ---------------------------

class UserInfo(BaseModel):
    user_id: int
    notify: bool = False

@mcp.tool()
async def send_notification(user: UserInfo, message: str) -> dict:
    """Sends a notification to a user if requested."""
    if user.notify:
        # Simulate sending notification
        print(f"Notifying user {user.user_id}: {message}")
        return {"status": "sent", "user_id": user.user_id}
    return {"status": "skipped", "user_id": user.user_id}

@mcp.tool()
def get_stock_price(ticker: str) -> float:
    """Gets the current price for a stock ticker."""
    # Replace with actual API call
    prices = {"AAPL": 180.50, "GOOG": 140.20}
    return prices.get(ticker.upper(), 0.0)

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# ----------------------- resorces ---------------------------

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Static resource returning simple text
@mcp.resource("config://app-version")
def get_app_version() -> str:
    """Returns the application version."""
    return "v2.1.0"

# Dynamic resource template expecting a 'user_id' from the URI
@mcp.resource("db://users/{user_id}/email")
async def get_user_email(user_id: str) -> str:
    """Retrieves the email address for a given user ID."""
    # Replace with actual database lookup
    emails = {"123": "alice@example.com", "456": "bob@example.com"}
    return emails.get(user_id, "not_found@example.com")

# Resource returning JSON data
@mcp.resource("data://product-categories")
def get_categories() -> list[str]:
    """Returns a list of available product categories."""
    return ["Electronics", "Books", "Home Goods"]


# ----------------------- prompts ---------------------------

@mcp.prompt()
def ask_review(code_snippet: str) -> str:
    """Generates a standard code review request."""
    return f"Please review the following code snippet for potential bugs and style issues:\n```python\n{code_snippet}\n```"

@mcp.prompt()
def debug_session_start(error_message: str) -> list[Message]:
    """Initiates a debugging help session."""
    return [
        UserMessage(f"I encountered an error:\n{error_message}"),
        AssistantMessage("Okay, I can help with that. Can you provide the full traceback and tell me what you were trying to do?")
    ]


# ----------------------- context ---------------------------


@mcp.resource("system://status")
async def get_system_status(ctx: Context) -> dict:
    """Checks system status and logs information."""
    await ctx.info("Checking system status...")
    # Perform checks
    await ctx.report_progress(1, 1) # Report completion
    return {"status": "OK", "load": 0.5, "client": ctx.client_id}

@mcp.tool()
async def process_large_file(file_uri: str, ctx: Context) -> str:
    """Processes a large file, reporting progress and reading resources."""
    await ctx.info(f"Starting processing for {file_uri}")
    # Read the resource using the context
    file_content_resource = await ctx.read_resource(file_uri)
    file_content = file_content_resource[0].content # Assuming single text content
    lines = file_content.splitlines()
    total_lines = len(lines)

    for i, line in enumerate(lines):
        # Process line...
        if (i + 1) % 100 == 0: # Report progress every 100 lines
            await ctx.report_progress(i + 1, total_lines)

    await ctx.info(f"Finished processing {file_uri}")
    return f"Processed {total_lines} lines."

if __name__ == "__main__":
    mcp.run(transport='sse')