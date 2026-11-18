const chatPanel = document.querySelector("#eos-chat");
const chatFrame = chatPanel?.querySelector("iframe");
const chatToggle = document.querySelector("#eos-chat-toggle");
const draftButton = document.querySelector(".use-chat-draft");

if (chatToggle && chatPanel) {
  const narrowScreen = window.matchMedia("(max-width: 1000px)");

  function setChatExpanded(expanded) {
    const label = expanded ? "Zbaliť chat Claude" : "Otvoriť chat Claude";
    chatPanel.hidden = !expanded;
    document.body.classList.toggle("chat-collapsed", !expanded);
    chatToggle.setAttribute("aria-expanded", String(expanded));
    chatToggle.setAttribute("aria-label", label);
    chatToggle.title = label;
    chatToggle.textContent = expanded ? "→" : "←";
  }

  setChatExpanded(!narrowScreen.matches);
  narrowScreen.addEventListener("change", (event) => setChatExpanded(!event.matches));
  chatToggle.addEventListener("click", () => {
    setChatExpanded(chatPanel.hidden);
  });
}

if (chatFrame) {
  function updateDraftAvailability() {
    chatFrame.contentWindow.postMessage({
      type: "eos-draft-availability",
      available: Boolean(document.querySelector("#quote-email-body")),
    }, location.origin);
  }

  function boostPageLinks() {
    const page = document.querySelector("#eos-page");
    if (!page || !window.htmx) return;
    const detail = /^\/(?:zakazka|ponuka|objednavka)\/[^/]+(?:\/odoslat)?$/;
    const pages = new Set(["/", "/nova", "/gmail", "/ponuky", "/objednavky",
                           "/sklad", "/dodavatelia", "/kb", "/stav", "/model"]);
    for (const link of page.querySelectorAll("main a[href]:not([target]):not([download]):not([hx-boost])")) {
      const url = new URL(link.href, location.href);
      if (url.origin !== location.origin || url.hash || (!pages.has(url.pathname) && !detail.test(url.pathname))) continue;
      link.setAttribute("hx-boost", "true");
      link.setAttribute("hx-target", "#eos-page");
      link.setAttribute("hx-select", "#eos-page");
      link.setAttribute("hx-swap", "outerHTML show:window:top");
      window.htmx.process(link);
    }
  }

  boostPageLinks();
  document.addEventListener("htmx:load", boostPageLinks);
  chatFrame.addEventListener("load", updateDraftAvailability);
  document.addEventListener("htmx:afterSettle", updateDraftAvailability);
  document.addEventListener("htmx:historyRestore", updateDraftAvailability);

  const recent = sessionStorage.getItem("eos-chat-session");
  if (recent && /^[a-f0-9]{32}$/.test(recent)) chatFrame.src = "/chat?session=" + recent;

  window.addEventListener("message", (event) => {
    if (event.origin !== location.origin || event.source !== chatFrame.contentWindow) return;

    if (event.data?.type === "eos-chat-session") {
      if (event.data.id) sessionStorage.setItem("eos-chat-session", event.data.id);
      else sessionStorage.removeItem("eos-chat-session");
    }

    const emailBody = document.querySelector("#quote-email-body");
    if (!emailBody || event.data?.type !== "eos-quote-draft" || typeof event.data.text !== "string") return;
    if (emailBody.value && !window.confirm("Nahradiť vlastný text e-mailu návrhom od Clauda?")) return;
    emailBody.value = event.data.text;
    emailBody.focus();
    if (window.matchMedia("(max-width: 1000px)").matches && !chatPanel.hidden) {
      chatToggle.click();
    }
  });
}

if (window.parent !== window) {
  const session = document.body.dataset.chatSession || "";
  window.parent.postMessage({type: "eos-chat-session", id: session}, location.origin);
}

if (draftButton && window.parent !== window) {
  window.addEventListener("message", (event) => {
    if (event.origin === location.origin && event.source === window.parent &&
        event.data?.type === "eos-draft-availability") draftButton.hidden = !event.data.available;
  });

  draftButton.addEventListener("click", () => {
    const text = draftButton.closest("article").querySelector(".chat-text").textContent;
    window.parent.postMessage({type: "eos-quote-draft", text}, location.origin);
  });
}

const chatMessages = document.querySelector(".chat-messages");
if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;

const chatComposer = document.querySelector('form[action="/chat"]');
chatComposer?.addEventListener("submit", () => {
  const button = chatComposer.querySelector(".chat-send");
  button.disabled = true;
  button.textContent = "…";
  button.setAttribute("aria-label", "Claude pripravuje odpoveď");
});
