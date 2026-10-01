(function () {
    "use strict";

    function csrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute("content") : "";
    }

    async function api(url, options) {
        const opts = options || {};
        const headers = {
            Accept: "application/json",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrfToken(),
            ...(opts.headers || {}),
        };
        const response = await fetch(url, { ...opts, headers });
        const payload = await response.json().catch(() => ({}));
        return { response, payload };
    }

    function showError(message) {
        const el = document.getElementById("form-error");
        if (!el) {
            return;
        }
        el.hidden = !message;
        el.textContent = message || "";
    }

    function showSuccess(message) {
        const el = document.getElementById("form-success");
        if (!el) {
            return;
        }
        el.hidden = !message;
        el.textContent = message || "";
    }

    const root = document.getElementById("dictionary-create-workspace");
    if (!root || root.dataset.activeTab !== "source") {
        return;
    }

    const sourceTypes = JSON.parse(root.dataset.sourceTypes || "[]");
    const typeSelect = document.getElementById("new-source-type");
    typeSelect.innerHTML = "";
    sourceTypes.forEach(function (value) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        typeSelect.appendChild(option);
    });

    document.getElementById("create-source").addEventListener("click", async function () {
        const title = document.getElementById("new-source-title").value.trim();
        const url = document.getElementById("new-source-url").value.trim();
        const { response, payload } = await api("/admin/dictionary/sources", {
            method: "POST",
            body: JSON.stringify({
                source_type: typeSelect.value,
                title: title,
                url: url || null,
            }),
        });
        if (!response.ok) {
            showSuccess("");
            showError(payload.message || "Unable to create source.");
            return;
        }
        showError("");
        showSuccess(`Created source "${payload.source.title}".`);
        document.getElementById("new-source-title").value = "";
        document.getElementById("new-source-url").value = "";
    });
})();
