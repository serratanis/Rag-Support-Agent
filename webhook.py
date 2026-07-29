from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chatbot import get_response

app = FastAPI()

# We serve the widget.js file from the backend -> the front-end/web team
# does not have to host the file separately:
# https://YOUR-DOMAIN/static/widget.js
app.mount("/static", StaticFiles(directory="static"), name="static")

# IMPORTANT: "*" is only for development/testing. Before going live,
# restrict it to your real domain name like allow_origins=["https://your-domain.com"].
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str


@app.post("/chat")
async def chat(payload: ChatRequest):
    print("Incoming message:", payload.message, "| Session:", payload.session_id)

    reply = get_response(payload.message, payload.session_id)

    print("Bot response:", reply)

    return {"reply": reply}
