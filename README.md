# RAG-Powered Support Chatbot (Turkish, self-hosted LLM)

An embeddable website chat widget backed by a FastAPI webhook, a local
LLM (via [Ollama](https://ollama.com)), and a Retrieval-Augmented
Generation (RAG) knowledge base built with LangChain + Chroma.

Built for a B2B partner portal use case: users ask natural-language
questions about their account ("where do I see my invoices?", "how do
I update my IBAN?") and the bot answers **only from a defined
knowledge base**, always pointing to the correct page/link instead of
guessing — with hard guardrails so the model can never claim to have
performed a real action on the user's behalf.

> This is a genericized, company-independent version of a chatbot I
> built for a live production panel. All company-specific data, URLs,
> and branding have been replaced with placeholders/config so it can
> be shared publicly and reused for other clients.

## Features

- 💬 **Drop-in chat widget** (`static/widget.js`) — a single `<script>`
  tag embeds a floating chat bubble on any website, with a
  `window.CHAT_WIDGET_CONFIG` object for branding (colors, texts, API
  URL) — no build step required.
- 🧠 **RAG knowledge base** — answers are grounded in a `.txt` FAQ file
  chunked and embedded with a multilingual sentence-transformers model,
  stored in a local Chroma vector store.
- 🔒 **Prompt-injection resistant by design**:
  - A separate, low-cost LLM call classifies whether a message is even
    in-scope before the main model is invoked (cheap "intent guard").
  - The system prompt hard-refuses instructions to change the bot's
    role or ignore its rules.
  - A regex safety net catches any response that falsely implies the
    bot performed a real action ("I've saved/updated/confirmed that")
    and replaces it with a safe redirect to the correct page.
  - Deterministic keyword → URL matching strips out any wrong/stray
    links the LLM might hallucinate and inserts the correct one.
- 🗂️ **Per-session conversation memory** — recent messages (within a
  configurable timeout window) are stored in SQLite and replayed to
  the model for context continuity.
- ⚙️ **Fully config-driven** — company name, base URL, support link,
  phone number, and the whole keyword→page link map live in
  `config.json` (gitignored) / `config.example.json`, so the same
  codebase can be re-branded for any client in minutes.
- 🏠 **Runs on a local/self-hosted LLM** (via Ollama) — no per-token
  API costs, all data stays on your own infrastructure.

## Architecture

```
Website (widget.js)
       │  POST /chat { message, session_id }
       ▼
FastAPI webhook (webhook.py)
       │
       ▼
chatbot.py
   ├─ 1. Greeting / off-topic short-circuit
   ├─ 2. Intent guard (small LLM call, in-scope check)
   ├─ 3. RAG lookup (rag.py → Chroma vector store)
   ├─ 4. Main LLM call with retrieved context + chat history
   ├─ 5. Safety filters (prompt-leak / fake-action / wrong-link)
   └─ 6. Save turn to SQLite (database.py)
       │
       ▼
Ollama (local LLM server, e.g. qwen3:1.7b)
```

## Setup

1. **Install [Ollama](https://ollama.com)** and pull a model:
   ```bash
   ollama pull qwen3:1.7b
   ```
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Add your knowledge base**: put one or more `.txt` files with
   Q&A pairs into `knowledge_base/` (see `faq_example.txt` for the
   expected format).
4. **Configure your brand**: copy `config.example.json` to
   `config.json` and fill in your real company name, domain, support
   link, phone number, and page links.
   ```bash
   cp config.example.json config.json
   ```
5. **Run it**:
   ```bash
   python app.py
   ```
   This starts Ollama if it isn't already running, then serves the
   API at `http://localhost:8002`.
6. **Try it**: open `test.html` in a browser (it points at
   `localhost:8002` by default) and chat with the bubble in the
   bottom-right corner.

## Embedding on a real website

```html
<script>
  window.CHAT_WIDGET_CONFIG = {
    apiUrl: "https://your-backend-domain.com/chat",
    title: "Support Chat",
    subtitle: "We usually reply within seconds",
    greeting: "Hi! How can I help you?",
    primaryColor: "#2b6cd9"
  };
</script>
<script src="https://your-backend-domain.com/static/widget.js"></script>
```

Before going live, lock down CORS in `webhook.py`
(`allow_origins=["https://your-real-domain.com"]`) instead of `"*"`.

## Tech stack

- **FastAPI** — webhook / REST API
- **Ollama** — local LLM inference (tested with `qwen3:1.7b`)
- **LangChain + Chroma** — document chunking, embeddings, vector search
- **sentence-transformers** (multilingual MiniLM) — embeddings
- **SQLite** — lightweight conversation history store
- **Vanilla JS** — zero-dependency embeddable widget

## Notes / limitations

- This project targets Turkish-language support flows, but the
  architecture (intent guard → RAG → grounded generation → safety
  filters) is language-agnostic; swap the system prompt and knowledge
  base to adapt it to another language or domain.
- `config.json`, the SQLite database, and the vector store are
  gitignored on purpose — they may contain real customer data in a
  production deployment and should never be committed.

## License

MIT — see [LICENSE](LICENSE).
