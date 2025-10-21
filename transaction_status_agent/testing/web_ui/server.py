from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from google.genai import types
from transaction_status_agent.runner import create_runner
from transaction_status_agent.config import DEFAULT_USER_ID, APP_NAME
from transaction_status_agent.prompts.transaction_status_prompt import TRANSACTION_STATUS_PROMPT
import os

# --- Global state ---
runner = None
current_prompt = TRANSACTION_STATUS_PROMPT
active_session = None

# --- Lifespan (startup + teardown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize runner and global session once on startup, close cleanly on shutdown."""
    global runner, active_session
    print("🚀 Initializing ADK runner...")
    runner = await create_runner(instruction_override=current_prompt)
    print("✅ Runner ready.")

    # ✅ Create global session at startup so memory persists across messages
    active_session = await runner.session_service.create_session(
        state={"user_id": DEFAULT_USER_ID},
        app_name=APP_NAME,
        user_id=DEFAULT_USER_ID,
    )
    print(f"🧠 Global session created: {active_session.id}")

    yield


# --- Create FastAPI app ---
app = FastAPI(title="Ops Agent Playground", lifespan=lifespan)

# --- Serve static frontend ---
frontend_dir = os.path.join(os.path.dirname(__file__), "static")
print(f"🔍 Serving frontend from: {frontend_dir}")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the frontend HTML UI."""
    with open(os.path.join(frontend_dir, "index.html")) as f:
        html = f.read()
    html = html.replace("{{PROMPT}}", current_prompt)
    return HTMLResponse(content=html)


@app.post("/update_prompt", response_class=JSONResponse)
async def update_prompt(request: Request):
    """Update the system prompt and rebuild the runner cleanly, preserving session."""
    global runner, current_prompt, active_session
    data = await request.json()
    new_prompt = data.get("prompt", "").strip()

    if not new_prompt:
        return {"status": "error", "message": "Prompt cannot be empty."}

    current_prompt = new_prompt

    # Recreate runner with updated prompt (session persists)
    runner = await create_runner(instruction_override=current_prompt)
    print("🔁 Runner rebuilt with updated prompt.")

    # Reuse or recreate session if it was cleared
    if not active_session:
        active_session = await runner.session_service.create_session(
            state={"user_id": DEFAULT_USER_ID},
            app_name=APP_NAME,
            user_id=DEFAULT_USER_ID,
        )
        print(f"🧠 New session created: {active_session.id}")

    return {"status": "success", "message": "Prompt updated successfully."}


@app.post("/run", response_class=JSONResponse)
async def run_message(request: Request):
    """Handle user queries — preserve conversation and return model reply."""
    global runner, active_session
    body = await request.json()
    query = body.get("query", "").strip()

    if not query:
        return {"response": "(empty query)"}

    # Ensure persistent session
    if active_session is None:
        active_session = await runner.session_service.create_session(
            state={"user_id": DEFAULT_USER_ID},
            app_name=APP_NAME,
            user_id=DEFAULT_USER_ID,
        )
        print(f"🧠 Session created: {active_session.id}")

    content = types.Content(role="user", parts=[types.Part(text=query)])
    reply = ""

    async for event in runner.run_async(
        session_id=active_session.id,
        user_id=active_session.user_id,
        new_message=content,
    ):

        if getattr(event, "content", None):
            for part in getattr(event.content, "parts", []):
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    tool_name = fc.name
                    tool_args = fc.args
                    reply += f"[Tool call → {tool_name}({tool_args})] \n \n"

                elif hasattr(part, "function_response") and part.function_response:
                    fr = part.function_response
                    print(f"\n⚙️ Tool executed: {fr.name}")
                    print(f"↳ Tool output: {getattr(fr, 'response', {})}")

                elif hasattr(part, "text") and part.text:
                    role = getattr(event.content, "role", "unknown")
                    if role in ("model", "assistant"):
                        reply += part.text.strip() + " "

    final_reply = reply.strip() or "(no reply)"
    print(f"🧩 FINAL REPLY: {final_reply!r}")
    return JSONResponse(content={"response": final_reply}, status_code=200)


@app.post("/reset_session", response_class=JSONResponse)
async def reset_session():
    """Clear the current chat session but keep the prompt."""
    global active_session
    active_session = None
    return {"status": "success", "message": "Session reset successfully."}
