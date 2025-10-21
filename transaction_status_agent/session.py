from google.adk.sessions import InMemorySessionService

_session_service = None

def get_session_service():
    global _session_service
    if _session_service is None:
        _session_service = InMemorySessionService()
    return _session_service
