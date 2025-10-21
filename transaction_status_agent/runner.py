from google.adk.runners import Runner
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from transaction_status_agent.builder import build_agent
from transaction_status_agent.config import APP_NAME
from transaction_status_agent.session import get_session_service

async def create_runner(instruction_override=None):
    artifact_service = InMemoryArtifactService()
    session_service = get_session_service()
    agent, _ = await build_agent(instruction_override)

    runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=session_service,
        artifact_service=artifact_service,
    )
    return runner
