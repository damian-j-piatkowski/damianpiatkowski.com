(function () {
    function debounce(fn, waitMs) {
        let timer = null;
        return function debounced(...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), waitMs);
        };
    }

    const searchInput = document.getElementById("dictionary-search");
    const resultsList = document.getElementById("dictionary-results");
    const statusEl = document.getElementById("dictionary-status");
    const page = document.querySelector(".dictionary-page");
    const isAdmin = page && page.dataset.isAdmin === "true";

    if (!searchInput || !resultsList) {
        return;
    }

    function setStatus(message) {
        if (!statusEl) {
            return;
        }
        if (!message) {
            statusEl.hidden = true;
            statusEl.textContent = "";
            return;
        }
        statusEl.hidden = false;
        statusEl.textContent = message;
    }

    function renderResults(results) {
        resultsList.innerHTML = "";
        if (!results.length) {
            setStatus("No matching entries.");
            return;
        }
        setStatus("");
        results.forEach((entry) => {
            const item = document.createElement("li");
            item.className = "dictionary-result-item";

            const textWrap = document.createElement("div");
            const term = document.createElement("div");
            term.className = "dictionary-result-term";
            term.textContent = entry.viet_word;
            const translation = document.createElement("div");
            translation.className = "dictionary-result-translation";
            translation.textContent = entry.english_translation;
            textWrap.appendChild(term);
            textWrap.appendChild(translation);
            item.appendChild(textWrap);

            if (isAdmin) {
                const editLink = document.createElement("a");
                editLink.className = "dictionary-edit-link";
                editLink.textContent = "Edit";
                editLink.href = `/admin/dictionary/${entry.id}/edit`;
                item.appendChild(editLink);
            }

            resultsList.appendChild(item);
        });
    }

    async function runSearch(query) {
        const trimmed = query.trim();
        if (!trimmed) {
            resultsList.innerHTML = "";
            setStatus("");
            return;
        }
        setStatus("Searching...");
        try {
            const response = await fetch(
                `/dictionary/search?q=${encodeURIComponent(trimmed)}`,
                { headers: { Accept: "application/json" } }
            );
            if (!response.ok) {
                throw new Error("Search failed");
            }
            const payload = await response.json();
            renderResults(payload.results || []);
        } catch (error) {
            setStatus("Unable to search right now.");
        }
    }

    const debouncedSearch = debounce(runSearch, 200);
    searchInput.addEventListener("input", (event) => {
        debouncedSearch(event.target.value);
    });
})();
