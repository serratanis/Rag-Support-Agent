/**
 * Embeddable Support Chat Widget
 * ------------------------------------
 * USAGE: Add the following lines to your site (WordPress/Wix/Shopify "custom code" area or
 * directly into HTML):
 *
 *   <script>
 *     window.CHAT_WIDGET_CONFIG = {
 *       apiUrl: "https://YOUR-BACKEND-ADDRESS/chat",
 *       title: "Support Chat",
 *       subtitle: "We usually reply within seconds",
 *       greeting: "Hello! How can I help you?",
 *       errorMessage: "I couldn't connect right now, please try again in a moment.",
 *       primaryColor: "#2b6cd9"
 *     };
 *   </script>
 *   <script src="widget.js"></script>
 *
 * Replace the `apiUrl` with the public (accessible via internet, with HTTPS)
 * address of the server where your backend is running. If it's only running on
 * your computer (localhost), visitors' browsers won't be able to access localhost
 * when you add it to the site - the backend must be live on a real server/hosting.
 */
(function () {
  const cfg = Object.assign(
    {
      apiUrl: "http://localhost:8002/chat",
      title: "Support Chat",
      subtitle: "We usually reply within seconds",
      greeting: "Hello! How can I help you?",
      errorMessage: "I couldn't connect right now, please try again in a moment.",
      primaryColor: "#2b6cd9",
      storageKey: "chat_widget_session"
    },
    window.CHAT_WIDGET_CONFIG || {}
  );

  // --- Session ID: keep the conversation going even if the visitor refreshes the page ---
  function getSessionId() {
    let id = localStorage.getItem(cfg.storageKey);
    if (!id) {
      id = "sess_" + Math.random().toString(36).slice(2) + Date.now();
      localStorage.setItem(cfg.storageKey, id);
    }
    return id;
  }

  // --- Style ---
  const style = document.createElement("style");
  style.textContent = `
    #cw-bubble {
      position: fixed; bottom: 24px; right: 24px; width: 60px; height: 60px;
      border-radius: 50%; background: ${cfg.primaryColor}; color: #fff; border: none;
      box-shadow: 0 4px 14px rgba(0,0,0,0.25); cursor: pointer; z-index: 999999;
      display: flex; align-items: center; justify-content: center; font-size: 28px;
      transition: transform 0.15s ease;
    }
    #cw-bubble:hover { transform: scale(1.06); }
    #cw-panel {
      position: fixed; bottom: 96px; right: 24px; width: 340px; max-width: 90vw;
      height: 460px; max-height: 70vh; background: #fff; border-radius: 14px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.2); display: none; flex-direction: column;
      overflow: hidden; z-index: 999999; font-family: -apple-system, Segoe UI, Roboto, sans-serif;
    }
    #cw-panel.open { display: flex; }
    #cw-header {
      background: ${cfg.primaryColor}; color: #fff; padding: 14px 16px; font-weight: 600;
      display: flex; justify-content: space-between; align-items: center; font-size: 15px;
    }
    #cw-header span.status { font-weight: 400; font-size: 12px; opacity: 0.85; display:block; }
    #cw-close { background: none; border: none; color: #fff; font-size: 20px; cursor: pointer; line-height: 1;}
    #cw-messages {
      flex: 1; overflow-y: auto; padding: 12px; background: #f5f7fa;
      display: flex; flex-direction: column; gap: 8px;
    }
    .cw-msg { max-width: 80%; padding: 8px 12px; border-radius: 12px; font-size: 14px; line-height: 1.4; word-wrap: break-word; }
    .cw-msg.user { align-self: flex-end; background: ${cfg.primaryColor}; color: #fff; border-bottom-right-radius: 3px; }
    .cw-msg.bot { align-self: flex-start; background: #fff; color: #222; border: 1px solid #e2e5ea; border-bottom-left-radius: 3px; }
    .cw-msg.bot a { color: ${cfg.primaryColor}; }
    #cw-input-row { display: flex; border-top: 1px solid #e2e5ea; padding: 8px; gap: 8px; }
    #cw-input {
      flex: 1; border: 1px solid #dfe3e8; border-radius: 20px; padding: 8px 14px;
      font-size: 14px; outline: none;
    }
    #cw-send {
      background: ${cfg.primaryColor}; color: #fff; border: none; border-radius: 50%;
      width: 36px; height: 36px; cursor: pointer; font-size: 16px;
    }
    #cw-send:disabled { opacity: 0.5; cursor: default; }
  `;
  document.head.appendChild(style);

  // --- HTML structure ---
  const bubble = document.createElement("button");
  bubble.id = "cw-bubble";
  bubble.setAttribute("aria-label", "Open support chat");
  bubble.innerHTML = "💬";

  const panel = document.createElement("div");
  panel.id = "cw-panel";
  panel.innerHTML = `
    <div id="cw-header">
      <div>${cfg.title}<span class="status">${cfg.subtitle}</span></div>
      <button id="cw-close" aria-label="Close">✕</button>
    </div>
    <div id="cw-messages"></div>
    <div id="cw-input-row">
      <input id="cw-input" type="text" placeholder="Type your message..." />
      <button id="cw-send" aria-label="Send">➤</button>
    </div>
  `;

  document.body.appendChild(bubble);
  document.body.appendChild(panel);

  const messagesEl = panel.querySelector("#cw-messages");
  const inputEl = panel.querySelector("#cw-input");
  const sendBtn = panel.querySelector("#cw-send");
  const closeBtn = panel.querySelector("#cw-close");

  function addMessage(text, sender) {
    const div = document.createElement("div");
    div.className = "cw-msg " + sender;
    // Simple link detection (makes https://... links from the backend clickable)
    div.innerHTML = text.replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank" rel="noopener">$1</a>'
    );
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  let welcomed = false;
  bubble.addEventListener("click", () => {
    panel.classList.toggle("open");
    if (panel.classList.contains("open") && !welcomed) {
      addMessage(cfg.greeting, "bot");
      welcomed = true;
      inputEl.focus();
    }
  });
  closeBtn.addEventListener("click", () => panel.classList.remove("open"));

  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text) return;
    addMessage(text, "user");
    inputEl.value = "";
    sendBtn.disabled = true;

    try {
      const res = await fetch(cfg.apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: getSessionId() }),
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      addMessage(data.reply, "bot");
    } catch (err) {
      console.error("Chat widget error:", err);
      addMessage(cfg.errorMessage, "bot");
    } finally {
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
  });
})();
