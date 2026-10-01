(function () {
    function debounce(fn, waitMs) {
        let timer = null;
        return function debounced(...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), waitMs);
        };
    }

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

    function fillSelect(selectEl, values, getLabel, getValue) {
        if (!selectEl) {
            return;
        }
        selectEl.innerHTML = "";
        values.forEach((value) => {
            const option = document.createElement("option");
            option.value = getValue ? getValue(value) : value;
            option.textContent = getLabel ? getLabel(value) : value;
            selectEl.appendChild(option);
        });
    }

    function renderChips(container, items, onRemove) {
        container.innerHTML = "";
        items.forEach((item) => {
            const chip = document.createElement("span");
            chip.className = "admin-chip";
            chip.textContent = item;
            const button = document.createElement("button");
            button.type = "button";
            button.setAttribute("aria-label", "Remove");
            button.textContent = "×";
            button.addEventListener("click", () => onRemove(item));
            chip.appendChild(button);
            container.appendChild(chip);
        });
    }

    const createRoot = document.getElementById("dictionary-create-workspace");
    const editRoot = document.getElementById("dictionary-edit-workspace");
    const root = createRoot || editRoot;
    if (!root) {
        return;
    }

    const mode = createRoot ? "create" : "edit";
    const availableWordTypes = JSON.parse(root.dataset.wordTypes || "[]");
    const availableSourceTypes = JSON.parse(root.dataset.sourceTypes || "[]");
    let recentSources = JSON.parse(root.dataset.recentSources || "[]");
    let selectedWordTypes = [];
    let pendingExamples = [];
    let wordId = null;
    let associatedRoots = [];

    const vietWordInput = document.getElementById("viet-word");
    const englishInput = document.getElementById("english-translation");
    const wordTypeSelect = document.getElementById("word-type-select");
    const selectedTypesEl = document.getElementById("selected-word-types");
    const exampleSourceSelect = document.getElementById("example-source");
    const newSourceTypeSelect = document.getElementById("new-source-type");
    const examplesList = document.getElementById("examples-list");
    const hanVietResults = document.getElementById("han-viet-results");
    const associatedRootsEl = document.getElementById("associated-roots");
    const duplicateBanner = document.getElementById("duplicate-banner");
    const duplicateMessage = document.getElementById("duplicate-message");
    const duplicateEditLink = document.getElementById("duplicate-edit-link");
    const checkRootsBtn = document.getElementById("check-roots");

    fillSelect(wordTypeSelect, availableWordTypes);
    fillSelect(newSourceTypeSelect, availableSourceTypes);

    function refreshSourceSelect() {
        fillSelect(
            exampleSourceSelect,
            recentSources,
            (source) => source.title,
            (source) => String(source.id)
        );
    }

    function refreshTypeChips() {
        renderChips(selectedTypesEl, selectedWordTypes, (removed) => {
            selectedWordTypes = selectedWordTypes.filter((type) => type !== removed);
            refreshTypeChips();
        });
    }

    function renderPendingExamples() {
        examplesList.innerHTML = "";
        pendingExamples.forEach((example, index) => {
            const row = document.createElement("div");
            row.className = "admin-chip";
            const source = recentSources.find((item) => String(item.id) === String(example.source_id));
            row.textContent = `${example.sentence} / ${example.english_translation}` +
                (source ? ` (${source.title})` : "");
            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.textContent = "×";
            removeBtn.addEventListener("click", async () => {
                if (example.id) {
                    const { response, payload } = await api(
                        `/admin/dictionary/examples/${example.id}`,
                        { method: "DELETE" }
                    );
                    if (!response.ok) {
                        showError(payload.message || "Unable to remove example.");
                        return;
                    }
                }
                pendingExamples.splice(index, 1);
                renderPendingExamples();
            });
            row.appendChild(removeBtn);
            examplesList.appendChild(row);
        });
    }

    function renderAssociatedRoots() {
        if (!associatedRootsEl) {
            return;
        }
        associatedRootsEl.innerHTML = "";
        associatedRoots.forEach((rootItem) => {
            const chip = document.createElement("span");
            chip.className = "admin-chip";
            chip.textContent = `${rootItem.root} (${rootItem.chinese_character})`;

            const unlinkBtn = document.createElement("button");
            unlinkBtn.type = "button";
            unlinkBtn.textContent = "Unlink";
            unlinkBtn.addEventListener("click", async () => {
                const { response, payload } = await api(
                    `/admin/dictionary/words/${wordId}/han-viet/${rootItem.id}`,
                    { method: "DELETE" }
                );
                if (!response.ok) {
                    showError(payload.message || "Unable to unlink root.");
                    return;
                }
                associatedRoots = associatedRoots.filter((item) => item.id !== rootItem.id);
                renderAssociatedRoots();
            });

            const deleteBtn = document.createElement("button");
            deleteBtn.type = "button";
            deleteBtn.textContent = "Delete root";
            deleteBtn.addEventListener("click", async () => {
                const { response, payload } = await api(
                    `/admin/dictionary/han-viet/${rootItem.id}`,
                    { method: "DELETE" }
                );
                if (response.status === 409) {
                    showError(`${payload.message} Use Unlink for this entry instead.`);
                    return;
                }
                if (!response.ok) {
                    showError(payload.message || "Unable to delete root.");
                    return;
                }
                associatedRoots = associatedRoots.filter((item) => item.id !== rootItem.id);
                renderAssociatedRoots();
            });

            chip.appendChild(unlinkBtn);
            chip.appendChild(deleteBtn);
            associatedRootsEl.appendChild(chip);
        });
    }

    document.getElementById("add-word-type").addEventListener("click", () => {
        const value = wordTypeSelect.value;
        if (!value || selectedWordTypes.includes(value)) {
            return;
        }
        selectedWordTypes.push(value);
        refreshTypeChips();
    });

    document.getElementById("add-example").addEventListener("click", async () => {
        const sentence = document.getElementById("example-sentence").value.trim();
        const englishTranslation = document.getElementById("example-translation").value.trim();
        const sourceId = exampleSourceSelect.value;
        if (!sentence || !englishTranslation || !sourceId) {
            showError("Example sentence, translation, and source are required.");
            return;
        }
        showError("");

        if (mode === "edit" && wordId) {
            const { response, payload } = await api(
                `/admin/dictionary/words/${wordId}/examples`,
                {
                    method: "POST",
                    body: JSON.stringify({
                        source_id: Number(sourceId),
                        sentence,
                        english_translation: englishTranslation,
                    }),
                }
            );
            if (!response.ok) {
                showError(payload.message || "Unable to add example.");
                return;
            }
            pendingExamples.push(payload.example);
        } else {
            pendingExamples.push({
                source_id: Number(sourceId),
                sentence,
                english_translation: englishTranslation,
            });
        }
        document.getElementById("example-sentence").value = "";
        document.getElementById("example-translation").value = "";
        renderPendingExamples();
    });

    document.getElementById("create-source").addEventListener("click", async () => {
        const sourceType = newSourceTypeSelect.value;
        const title = document.getElementById("new-source-title").value.trim();
        const url = document.getElementById("new-source-url").value.trim();
        const { response, payload } = await api("/admin/dictionary/sources", {
            method: "POST",
            body: JSON.stringify({
                source_type: sourceType,
                title,
                url: url || null,
            }),
        });
        if (!response.ok) {
            showError(payload.message || "Unable to create source.");
            return;
        }
        recentSources = [payload.source, ...recentSources];
        refreshSourceSelect();
        exampleSourceSelect.value = String(payload.source.id);
        document.getElementById("new-source-title").value = "";
        document.getElementById("new-source-url").value = "";
        showError("");
    });

    async function runDuplicateCheck(value) {
        if (!duplicateBanner) {
            return;
        }
        const trimmed = value.trim();
        if (!trimmed) {
            duplicateBanner.hidden = true;
            return;
        }
        const { response, payload } = await api(
            `/admin/dictionary/check-duplicate?viet_word=${encodeURIComponent(trimmed)}`
        );
        if (!response.ok || !payload.exists) {
            duplicateBanner.hidden = true;
            return;
        }
        duplicateBanner.hidden = false;
        duplicateMessage.textContent =
            `An entry for "${payload.entry.viet_word}" already exists.`;
        duplicateEditLink.href = `/admin/dictionary/${payload.entry.id}/edit`;
    }

    if (mode === "create") {
        const debouncedDuplicateCheck = debounce(runDuplicateCheck, 400);
        vietWordInput.addEventListener("input", (event) => {
            debouncedDuplicateCheck(event.target.value);
        });
    }

    async function renderHanVietCheck(compound) {
        const { response, payload } = await api(
            `/admin/dictionary/han-viet/check?word=${encodeURIComponent(compound)}`
        );
        if (!response.ok) {
            showError("Unable to check Hán Việt roots.");
            return;
        }
        hanVietResults.innerHTML = "";
        (payload.found || []).forEach((rootItem) => {
            const row = document.createElement("div");
            row.className = "admin-chip-row";
            const label = document.createElement("span");
            label.textContent =
                `Found: ${rootItem.root} (${rootItem.chinese_character}) — ${rootItem.root_meaning}`;
            const associateBtn = document.createElement("button");
            associateBtn.type = "button";
            associateBtn.className = "admin-btn";
            associateBtn.textContent = "Associate";
            associateBtn.disabled = !wordId;
            associateBtn.addEventListener("click", async () => {
                const result = await api(
                    `/admin/dictionary/words/${wordId}/han-viet/${rootItem.id}`,
                    { method: "POST" }
                );
                if (!result.response.ok) {
                    showError(result.payload.message || "Unable to associate root.");
                    return;
                }
                if (!associatedRoots.some((item) => item.id === rootItem.id)) {
                    associatedRoots.push(rootItem);
                    renderAssociatedRoots();
                }
            });
            row.appendChild(label);
            row.appendChild(associateBtn);
            hanVietResults.appendChild(row);
        });

        (payload.missing || []).forEach((missingRoot) => {
            const row = document.createElement("div");
            row.className = "admin-section";
            const title = document.createElement("p");
            title.innerHTML = `Missing root: <strong></strong>`;
            title.querySelector("strong").textContent = missingRoot;
            const chineseInput = document.createElement("input");
            chineseInput.placeholder = "Chinese character";
            const meaningInput = document.createElement("input");
            meaningInput.placeholder = "English meaning";
            const addBtn = document.createElement("button");
            addBtn.type = "button";
            addBtn.className = "admin-btn";
            addBtn.textContent = "Add New Hán Việt Root";
            addBtn.disabled = !wordId;
            addBtn.addEventListener("click", async () => {
                const result = await api(`/admin/dictionary/words/${wordId}/han-viet`, {
                    method: "POST",
                    body: JSON.stringify({
                        root: missingRoot,
                        chinese_character: chineseInput.value,
                        root_meaning: meaningInput.value,
                    }),
                });
                if (!result.response.ok) {
                    showError(result.payload.message || "Unable to create root.");
                    return;
                }
                associatedRoots.push(result.payload.root);
                renderAssociatedRoots();
                addBtn.disabled = true;
                addBtn.textContent = "Added";
            });
            row.appendChild(title);
            row.appendChild(chineseInput);
            row.appendChild(meaningInput);
            row.appendChild(addBtn);
            hanVietResults.appendChild(row);
        });
    }

    if (checkRootsBtn) {
        checkRootsBtn.addEventListener("click", () => {
            renderHanVietCheck(vietWordInput.value.trim());
        });
    }

    document.getElementById("save-entry").addEventListener("click", async () => {
        showError("");
        showSuccess("");
        const body = {
            viet_word: vietWordInput.value,
            english_translation: englishInput.value,
            word_types: selectedWordTypes,
        };

        if (mode === "create") {
            const { response, payload } = await api("/admin/dictionary/words", {
                method: "POST",
                body: JSON.stringify(body),
            });
            if (!response.ok) {
                showError(payload.message || "Unable to save entry.");
                return;
            }
            wordId = payload.entry.id;
            if (checkRootsBtn) {
                checkRootsBtn.disabled = false;
            }

            for (const example of pendingExamples) {
                const exampleResult = await api(
                    `/admin/dictionary/words/${wordId}/examples`,
                    {
                        method: "POST",
                        body: JSON.stringify(example),
                    }
                );
                if (!exampleResult.response.ok) {
                    showError(exampleResult.payload.message || "Entry saved, but an example failed.");
                    return;
                }
            }
            window.location.href = `/admin/dictionary/${wordId}/edit`;
            return;
        }

        const { response, payload } = await api(`/admin/dictionary/words/${wordId}`, {
            method: "PATCH",
            body: JSON.stringify(body),
        });
        if (!response.ok) {
            showError(payload.message || "Unable to save changes.");
            return;
        }
        showSuccess("Entry updated.");
    });

    const deleteBtn = document.getElementById("delete-entry");
    if (deleteBtn) {
        deleteBtn.addEventListener("click", async () => {
            const confirmed = window.confirm(
                "Delete this dictionary entry permanently? This cannot be undone."
            );
            if (!confirmed) {
                return;
            }
            const secondConfirm = window.confirm(
                "Secondary confirmation: are you sure you want to delete this entry?"
            );
            if (!secondConfirm) {
                return;
            }
            const { response, payload } = await api(`/admin/dictionary/words/${wordId}`, {
                method: "DELETE",
            });
            if (!response.ok) {
                showError(payload.message || "Unable to delete entry.");
                return;
            }
            window.location.href = "/dictionary";
        });
    }

    refreshSourceSelect();

    if (mode === "edit") {
        const word = JSON.parse(root.dataset.word || "{}");
        wordId = word.id;
        vietWordInput.value = word.viet_word || "";
        englishInput.value = word.english_translation || "";
        selectedWordTypes = Array.isArray(word.word_types) ? [...word.word_types] : [];
        pendingExamples = Array.isArray(word.examples) ? [...word.examples] : [];
        associatedRoots = Array.isArray(word.han_viet_roots) ? [...word.han_viet_roots] : [];
        refreshTypeChips();
        renderPendingExamples();
        renderAssociatedRoots();
        if (checkRootsBtn) {
            checkRootsBtn.disabled = false;
        }
    }
})();
