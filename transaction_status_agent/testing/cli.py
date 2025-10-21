import asyncio
from google.genai import types
from transaction_status_agent.runner import create_runner
from transaction_status_agent.config import DEFAULT_USER_ID, APP_NAME



async def main():
    runner = await create_runner()
    session = await runner.session_service.create_session(
        state={"user_id": DEFAULT_USER_ID}, app_name=APP_NAME, user_id=DEFAULT_USER_ID
    )

    print("💬 Type your message (or 'exit' to quit):")
    while True:
        query = input("You: ").strip()
        if query.lower() in {"exit", "quit"}:
            break

        content = types.Content(role="user", parts=[types.Part(text=query)])
        async for event in runner.run_async(
            session_id=session.id,
            user_id=session.user_id,
            new_message=content,
        ):
            if getattr(event, "content", None):
                for part in getattr(event.content, "parts", []):
                    if hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call
                        print(f"\n📥 Model requested tool: {fc.name} with args {fc.args}")

                    elif hasattr(part, "function_response") and part.function_response:
                        fr = part.function_response
                        print(f"\n⚙️ Tool executed: {fr.name}")
                        print(f"↳ Tool output: {getattr(fr, 'response', {})}")

                    elif hasattr(part, "text") and part.text:
                        role = getattr(event.content, "role", "unknown")
                        if role in ("model", "assistant"):
                            print(f"\n🧠 Model reply:\n{part.text.strip()}")

if __name__ == "__main__":
    asyncio.run(main())
