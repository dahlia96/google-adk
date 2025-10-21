from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from transaction_status_agent.prompts.transaction_status_prompt import TRANSACTION_STATUS_PROMPT
from transaction_status_agent.callbacks import inject_user_id, debug_after_tool
from transaction_status_agent.config import MODEL_NAME, MCP_SERVER_URL

async def build_agent(instruction_override=None):
    """Constructs and returns an ADK LlmAgent + its MCP toolset."""
    toolset = McpToolset(
        connection_params=SseConnectionParams(url=MCP_SERVER_URL)
    )

    agent = LlmAgent(
        model=MODEL_NAME,
        name="support_agent",
        instruction=instruction_override or TRANSACTION_STATUS_PROMPT,
        tools=[toolset],
        before_tool_callback=inject_user_id,
        after_tool_callback=debug_after_tool,
    )

    return agent, toolset
