function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function safeSnippetHtml(value) {
  return value;
}

function mountSearchForms() {
  document.querySelectorAll(".search-form").forEach((form) => {
    const input = form.querySelector("input[name='q']");
    const results = form.parentElement.querySelector(".results");
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const query = input.value.trim();
      const endpoint = form.dataset.endpoint;
      const response = await fetch(`${endpoint}?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      if (!data.results.length) {
        results.innerHTML = `<p class="empty">没有匹配结果</p>`;
        return;
      }
      results.innerHTML = data.results
        .map(
          (item) => `
            <article class="result-item">
              <div class="result-title">
                <span>${escapeHtml(item.id)} · ${escapeHtml(item.title)}</span>
                <span class="score">${Number(item.score).toFixed(2)}</span>
              </div>
              <div class="snippet">${safeSnippetHtml(item.snippet)}</div>
            </article>
          `,
        )
        .join("");
    });
  });
}

function appendMessage(log, role, html) {
  const message = document.createElement("div");
  message.className = `message ${role}`;
  message.innerHTML = html;
  log.appendChild(message);
  log.scrollTop = log.scrollHeight;
}

function mountChat() {
  const form = document.querySelector("#chat-form");
  if (!form) return;

  const input = document.querySelector("#chat-input");
  const log = document.querySelector("#chat-log");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    appendMessage(log, "user", escapeHtml(message));
    input.value = "";

    const response = await fetch("/v3/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();
    const toolHtml = data.tool_calls.length
      ? `<div class="tool-calls">${data.tool_calls
          .map(
            (call) => `<div class="tool-call">${escapeHtml(call.name)}(${escapeHtml(
              call.arguments.fname,
            )})<br>${escapeHtml(call.result_preview)}</div>`,
          )
          .join("")}</div>`
      : "";
    appendMessage(log, "agent", `${escapeHtml(data.answer)}${toolHtml}`);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  mountSearchForms();
  mountChat();
});
