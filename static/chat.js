const chatLog = document.getElementById("chatLog");
const form = document.getElementById("messageForm");
const input = document.getElementById("messageInput");
const modeSelect = document.getElementById("modeSelect");
const apiKeyField = document.getElementById("apiKeyField");
const apiKeyInput = document.getElementById("apiKeyInput");
const systemPromptEl = document.getElementById("systemPrompt");
const temperatureEl = document.getElementById("temperature");
const tempLabel = document.getElementById("tempLabel");
const clearBtn = document.getElementById("clearBtn");
const downloadBtn = document.getElementById("downloadBtn");

tempLabel.innerText = temperatureEl.value;

temperatureEl.addEventListener("input", () => {
  tempLabel.innerText = temperatureEl.value;
});

modeSelect.addEventListener("change", () => {
  if (modeSelect.value === "openai") apiKeyField.style.display = "block";
  else apiKeyField.style.display = "none";
});

function appendMessage(text, role = "assistant") {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  // basic newline -> <br>
  div.innerHTML = text.replace(/\n/g, "<br/>");
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function sendMessage(message) {
  const payload = {
    message,
    mode: modeSelect.value,
    api_key: apiKeyInput.value || undefined,
    system_prompt: systemPromptEl.value,
    temperature: temperatureEl.value,
  };

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    return data;
  } catch (e) {
    return { reply: "Network error: " + e.message };
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  appendMessage(text, "user");
  input.value = "";
  appendMessage("...", "assistant"); // temporary placeholder
  const lastPlaceholder = chatLog.querySelectorAll(".assistant.msg");
  const placeholder = lastPlaceholder[lastPlaceholder.length - 1];

  const response = await sendMessage(text);
  placeholder.remove();
  appendMessage(response.reply || "No reply returned", "assistant");
});

// Quick buttons
document.querySelectorAll(".quick").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const msg = btn.dataset.msg;
    input.value = msg;
    form.dispatchEvent(new Event("submit", { cancelable: true }));
  });
});

// Clear
clearBtn.addEventListener("click", async () => {
  await fetch("/api/clear", { method: "POST" });
  chatLog.innerHTML = "";
});

// Download conversation (simple approach: ask server for history; but we stored in session — use current displayed)
downloadBtn.addEventListener("click", () => {
  // Collect visible messages
  const items = [];
  document.querySelectorAll("#chatLog .msg").forEach((node) => {
    const role = node.classList.contains("user") ? "user" : "assistant";
    items.push({ role, content: node.innerText });
  });
  const blob = new Blob([JSON.stringify(items, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  downloadBtn.href = url;
  downloadBtn.download = "chat_history.json";
});
