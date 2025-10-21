from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any, Optional

def inject_user_id(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    """Injects user_id before every tool call."""
    print("=== BEFORE TOOL CALL ===")
    print(f"Tool name: {tool.name}")
    print(f"Raw args before injection: {args}")
    args["user_id"] = "user_12345"
    print(f"Args after injection: {args}")
    print("=========================")

def debug_after_tool(tool_request=None, tool_response=None, **_):
    """Logs the tool’s request/response for debugging."""
    print("\n=== AFTER TOOL CALL ===")
    print(f"Tool request: {tool_request}")
    print(f"Tool response: {tool_response}")
    print("=========================\n")
