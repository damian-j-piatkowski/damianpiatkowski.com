// highlight.js
function escapeHTML(str) {
  return str.replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
}

function highlightBash(code) {
  code = escapeHTML(code);
  return code
    .replace(/^(\S+@[^$]+[$#])/gm, '<span class="prompt">$1</span>')
    .replace(/(<span class="prompt">.*?[$#]\s*)([^\n]+)/g,
             '$1<span class="command">$2</span>')
    .replace(/^(?!.*<span class="prompt">)(.+)$/gm,
             '<span class="output">$1</span>');
}

function highlight(el) {
  if (!el.classList.contains("language-bash")) return;

  let raw = el.textContent;
  el.innerHTML = highlightBash(raw);
}

document.querySelectorAll("pre code.language-bash").forEach(highlight);