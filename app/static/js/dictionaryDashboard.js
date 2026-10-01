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
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrfToken(),
            ...(opts.headers || {}),
        };
        const response = await fetch(url, { ...opts, headers });
        const payload = await response.json().catch(() => ({}));
        return { response, payload };
    }

    function initSourceDeletes() {
        document.querySelectorAll(".js-delete-source").forEach(function (button) {
            button.addEventListener("click", async function () {
                const sourceId = button.getAttribute("data-source-id");
                if (!sourceId) {
                    return;
                }
                if (!window.confirm("Delete this source and its citation sentences?")) {
                    return;
                }
                const { response, payload } = await api(
                    `/admin/dictionary/sources/${sourceId}`,
                    { method: "DELETE" }
                );
                if (!response.ok) {
                    window.alert(payload.message || "Failed to delete source.");
                    return;
                }
                const row = button.closest("tr");
                if (row) {
                    row.remove();
                }
            });
        });
    }

    function chartColors() {
        const styles = getComputedStyle(document.documentElement);
        return {
            fill: styles.getPropertyValue("--accent-primary").trim() || "#D0F0C0",
            line: styles.getPropertyValue("--accent-primary-hover").trim() || "#a0d08c",
        };
    }

    async function loadVelocity(rangeKey, chart) {
        const { response, payload } = await api(
            `/admin/api/stats/word-velocity?range=${encodeURIComponent(rangeKey)}`
        );
        if (!response.ok) {
            return;
        }
        chart.data.labels = payload.labels || [];
        chart.data.datasets[0].data = payload.counts || [];
        chart.update();
    }

    function initVelocityChart() {
        const canvas = document.getElementById("word-velocity-chart");
        if (!canvas || typeof Chart === "undefined") {
            return;
        }

        const colors = chartColors();
        const chart = new Chart(canvas.getContext("2d"), {
            type: "line",
            data: {
                labels: [],
                datasets: [
                    {
                        label: "Words created",
                        data: [],
                        fill: true,
                        tension: 0.25,
                        borderColor: colors.line,
                        backgroundColor: colors.fill,
                        pointRadius: 2,
                        pointHoverRadius: 4,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                    },
                },
                plugins: {
                    legend: { display: false },
                },
            },
        });

        const toggles = document.querySelectorAll(".admin-range-toggles [data-range]");
        toggles.forEach(function (button) {
            button.addEventListener("click", function () {
                toggles.forEach(function (btn) {
                    btn.classList.remove("is-active");
                });
                button.classList.add("is-active");
                loadVelocity(button.getAttribute("data-range"), chart);
            });
        });

        loadVelocity("30d", chart);
    }

    document.addEventListener("DOMContentLoaded", function () {
        initSourceDeletes();
        initVelocityChart();
    });
})();
