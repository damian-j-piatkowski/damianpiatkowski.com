(function () {
    "use strict";

    var POLL_MS = 10000;

    function csrfToken() {
        var meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute("content") : "";
    }

    async function api(url, options) {
        var opts = options || {};
        var headers = {
            Accept: "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrfToken(),
        };
        if (opts.headers) {
            Object.keys(opts.headers).forEach(function (key) {
                headers[key] = opts.headers[key];
            });
        }
        var response = await fetch(url, Object.assign({}, opts, { headers: headers }));
        var payload = await response.json().catch(function () {
            return {};
        });
        return { response: response, payload: payload };
    }

    function severityClass(value) {
        if (value > 85) {
            return "is-critical";
        }
        if (value >= 70) {
            return "is-warn";
        }
        return "is-ok";
    }

    function updateMetric(prefix, value) {
        var kpi = document.getElementById("kpi-" + prefix);
        var bar = document.getElementById("bar-" + prefix);
        if (!kpi || !bar) {
            return;
        }
        var numeric = typeof value === "number" ? value : 0;
        kpi.textContent = numeric.toFixed(1) + "%";
        bar.style.width = Math.max(0, Math.min(100, numeric)) + "%";
        bar.classList.remove("is-ok", "is-warn", "is-critical");
        bar.classList.add(severityClass(numeric));
    }

    async function refreshLive() {
        var result = await api("/admin/api/system-health/stats");
        if (!result.response.ok) {
            return;
        }
        var data = result.payload;
        updateMetric("cpu", data.cpu_percent);
        updateMetric("ram", data.ram_percent);
        updateMetric("swap", data.swap_percent);
        updateMetric("disk", data.disk_percent);

        var env = document.getElementById("system-health-env");
        var os = document.getElementById("system-health-os");
        var uptime = document.getElementById("system-health-uptime");
        if (env) {
            env.textContent = data.environment || "—";
            env.classList.toggle("is-mock", data.environment === "DEV MOCK");
            env.classList.toggle("is-prod", data.environment === "PRODUCTION");
        }
        if (os) {
            os.textContent = data.os_info || "—";
        }
        if (uptime) {
            uptime.textContent = "Uptime: " + (data.uptime || "—");
        }
    }

    function initLive() {
        var root = document.querySelector("[data-system-health-live]");
        if (!root) {
            return;
        }
        refreshLive();
        window.setInterval(refreshLive, POLL_MS);
    }

    function chartColors() {
        var styles = getComputedStyle(document.documentElement);
        return {
            cpu: styles.getPropertyValue("--accent-primary-hover").trim() || "#a0d08c",
            ram: styles.getPropertyValue("--accent-primary").trim() || "#D0F0C0",
        };
    }

    async function loadHistory(rangeKey, chart) {
        var result = await api(
            "/admin/api/system-health/history?range=" + encodeURIComponent(rangeKey)
        );
        if (!result.response.ok) {
            return;
        }
        var payload = result.payload;
        chart.data.labels = payload.labels || [];
        chart.data.datasets[0].data = payload.cpu || [];
        chart.data.datasets[1].data = payload.ram || [];
        chart.update();
    }

    function initTrends() {
        var root = document.querySelector("[data-system-health-trends]");
        var canvas = document.getElementById("system-health-chart");
        if (!root || !canvas || typeof Chart === "undefined") {
            return;
        }

        var colors = chartColors();
        var chart = new Chart(canvas.getContext("2d"), {
            type: "line",
            data: {
                labels: [],
                datasets: [
                    {
                        label: "CPU %",
                        data: [],
                        fill: false,
                        tension: 0.25,
                        borderColor: colors.cpu,
                        pointRadius: 2,
                        pointHoverRadius: 4,
                    },
                    {
                        label: "RAM %",
                        data: [],
                        fill: false,
                        tension: 0.25,
                        borderColor: colors.ram,
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
                        suggestedMax: 100,
                    },
                },
                plugins: {
                    legend: { display: true },
                },
            },
        });

        var toggles = document.querySelectorAll(".admin-range-toggles [data-range]");
        toggles.forEach(function (button) {
            button.addEventListener("click", function () {
                toggles.forEach(function (btn) {
                    btn.classList.remove("is-active");
                });
                button.classList.add("is-active");
                loadHistory(button.getAttribute("data-range"), chart);
            });
        });

        loadHistory("24h", chart);
    }

    document.addEventListener("DOMContentLoaded", function () {
        initLive();
        initTrends();
    });
})();
