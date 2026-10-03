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
        const payload = await response.json().catch(function () {
            return {};
        });
        return { response: response, payload: payload };
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
    if (!root || root.dataset.activeTab !== "han-viet") {
        return;
    }

    document.getElementById("create-han-viet-root").addEventListener("click", async function () {
        const syllable = document.getElementById("han-viet-root").value.trim();
        const chinese = document.getElementById("han-viet-chinese").value.trim();
        const meaning = document.getElementById("han-viet-meaning").value.trim();
        const { response, payload } = await api("/admin/dictionary/han-viet", {
            method: "POST",
            body: JSON.stringify({
                root: syllable,
                chinese_character: chinese,
                root_meaning: meaning,
            }),
        });
        if (!response.ok) {
            showSuccess("");
            showError(payload.message || "Unable to create Hán Việt root.");
            return;
        }
        showError("");
        showSuccess(
            `Created root "${payload.root.root}" (${payload.root.chinese_character}).`
        );
        document.getElementById("han-viet-root").value = "";
        document.getElementById("han-viet-chinese").value = "";
        document.getElementById("han-viet-meaning").value = "";
    });
})();
