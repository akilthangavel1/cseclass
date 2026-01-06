(function () {
  const root = document.querySelector("[data-chat]");
  if (!root) return;

  const messagesEl = root.querySelector("[data-chat-messages]");
  const typingEl = root.querySelector("[data-chat-typing]");
  const form = root.querySelector("[data-chat-form]");
  const input = root.querySelector('input[name="message"]');

  function getCookie(name) {
    const m = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return m ? decodeURIComponent(m[2]) : null;
  }

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function renderBubble(sender, text, timestamp) {
    const bubble = document.createElement("div");
    bubble.className = `bubble ${sender === "user" ? "bubble-user" : "bubble-bot"}`;
    const p = document.createElement("p");
    p.className = "bubble-text";
    p.textContent = text;
    const meta = document.createElement("div");
    meta.className = "bubble-meta";
    meta.textContent = timestamp ? timestamp : "";
    bubble.appendChild(p);
    bubble.appendChild(meta);
    messagesEl.appendChild(bubble);
    scrollToBottom();
  }

  function setTyping(on) {
    typingEl.hidden = !on;
    if (on) scrollToBottom();
  }

  async function loadHistory() {
    try {
      const res = await fetch("/chatbot/api/history/", { headers: { Accept: "application/json" } });
      if (!res.ok) return;
      const data = await res.json();
      const items = Array.isArray(data.messages) ? data.messages : [];
      if (items.length === 0) {
        renderBubble("bot", "Hello. How can I help today?", new Date().toISOString().slice(0, 16).replace("T", " "));
        return;
      }
      items.forEach((m) => renderBubble(m.sender, m.message, m.timestamp));
    } catch (e) {
      renderBubble("bot", "Hello. How can I help today?", new Date().toISOString().slice(0, 16).replace("T", " "));
    }
  }

  async function sendMessage(message) {
    const csrf = getCookie("csrftoken");
    setTyping(true);
    try {
      const res = await fetch("/chatbot/api/message/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          "X-CSRFToken": csrf || "",
        },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      setTyping(false);
      if (res.ok && data.reply) {
        const ts = data.timestamp ? data.timestamp.slice(0, 16).replace("T", " ") : "";
        renderBubble("bot", data.reply, ts);
        if (data.suggested_action === "book_appointment") {
          const a = document.createElement("a");
          a.href = "/appointments/book/";
          a.className = "btn btn-secondary";
          a.textContent = "Book appointment";
          const wrap = document.createElement("div");
          wrap.style.marginTop = "10px";
          wrap.appendChild(a);
          const last = messagesEl.lastElementChild;
          if (last) last.appendChild(wrap);
          scrollToBottom();
        }
      } else {
        renderBubble("bot", "Sorry, I couldn’t process that. Please try again.", "");
      }
    } catch (e) {
      setTyping(false);
      renderBubble("bot", "Network issue. Please try again.", "");
    }
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const msg = (input.value || "").trim();
    if (!msg) return;
    input.value = "";
    renderBubble("user", msg, new Date().toISOString().slice(0, 16).replace("T", " "));
    sendMessage(msg);
    input.focus();
  });

  loadHistory();
})();

