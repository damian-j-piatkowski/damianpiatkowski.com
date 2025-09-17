// highlight.js
/**
 * Lightweight custom syntax highlighter for blog code blocks.
 *
 * Features:
 *  - Escapes unsafe HTML
 *  - Highlights Bash prompts, commands, and outputs
 *  - Highlights Python keywords, strings, comments, and decorators
 *
 * Limitations:
 *  - Simple regex-based (not a full parser)
 *  - Intended for blog-sized snippets (up to ~100 lines)
 *
 * Usage:
 *  - Include this script in your blog
 *  - Mark code blocks with <pre><code class="language-python">...</code></pre>
 *  - Runs automatically on DOMContentLoaded
 */
const Highlighter = (() => {
  /**
   * Escape raw HTML characters so code displays safely in <pre><code>.
   * @param {string} str - Raw code string.
   * @returns {string} Escaped string safe for innerHTML.
   */
  function escapeHTML(str) {
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;");
  }

  /**
   * Highlight Bash code:
   *  - Prompts (`user@host$`)
   *  - Commands typed after the prompt
   *  - Output lines without a prompt
   * @param {string} code - Raw Bash code.
   * @returns {string} HTML with <span> wrappers.
   */
  function highlightBash(code) {
    code = escapeHTML(code);
    return code
      .replace(/^(\S+@[^$]+[$#])/gm, '<span class="prompt">$1</span>')
      .replace(/(<span class="prompt">.*?[$#]\s*)([^\n]+)/g, '$1<span class="command">$2</span>')
      .replace(/^(?!.*<span class="prompt">)(.+)$/gm, '<span class="output">$1</span>');
  }

  /**
   * Highlight Python code:
   *  - Keywords (def, class, return, etc.)
   *  - Strings (single, double, triple quotes)
   *  - Comments (# ...)
   *  - Decorators (@something)
   *  - Exception blocks (try, except, finally)
   *
   * Uses a single master regex to avoid overlapping replacements.
   * @param {string} code - Raw Python code.
   * @returns {string} HTML with <span> wrappers.
   */
  function highlightPython(code) {
    code = escapeHTML(code);

    const tokenRegex =
      /("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|#.*$|^\s*@\w+|\b(?:def|class|return|import|from|as|if|elif|else|for|while|with|pass|break|continue|and|or|not|is|in|None|True|False|yield|raise|try|except|finally)\b)/gm;

    return code.replace(tokenRegex, match => {
      if (match.startsWith("#")) {
        return `<span class="comment">${match}</span>`;
      }
      if (/^("""|'''|".*"|'.*')/.test(match)) {
        return `<span class="string">${match}</span>`;
      }
      if (/^\s*@\w+/.test(match)) {
        return `<span class="decorator">${match}</span>`;
      }
      if (/^(try|except|finally)$/.test(match)) {
        return `<span class="error-block">${match}</span>`;
      }
      return `<span class="keyword">${match}</span>`;
    });
  }

  /**
   * Map language CSS class → highlighter function.
   * Extend this object to support more languages.
   */
  const highlighters = {
    "language-bash": highlightBash,
    "language-python": highlightPython
  };

  /**
   * Apply highlighting to a single <code> block.
   * @param {HTMLElement} el - A <code> element inside <pre>.
   */
  function highlight(el) {
    const raw = el.textContent;
    for (const cls in highlighters) {
      if (el.classList.contains(cls)) {
        el.innerHTML = highlighters[cls](raw);
        break;
      }
    }
  }

  /**
   * Initialize highlighting on all <pre><code> blocks.
   * Runs automatically once DOM is ready.
   */
  function init() {
    document.querySelectorAll("pre code").forEach(highlight);
  }

  // Public API
  return { init };
})();

// Auto-run on DOM ready
document.addEventListener("DOMContentLoaded", Highlighter.init);