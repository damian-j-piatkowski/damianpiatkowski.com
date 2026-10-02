# System Health

Admin System Health provides live node metrics and historical CPU/RAM trends at
`/admin/system-health`. Live values poll `/admin/api/system-health/stats` every
10 seconds. Trends load Chart.js series from
`/admin/api/system-health/history?range=…`.

## Snapshot cron

Production should capture a 15-minute snapshot that persists metrics, optionally
emails a threshold alert (CPU > 90%, RAM > 85%, or Disk > 90%, with a one-hour
cooldown), and prunes logs older than 180 days:

```bash
*/15 * * * * cd /path/to/app && /path/to/venv/bin/flask health process-snapshot > /dev/null 2>&1
```

Ensure `FLASK_APP` and production environment variables are available to cron
(for example via a wrapper that sources the production `.env`).

In development, `flask health process-snapshot` is a no-op for persistence so
local Windows/cron dry-runs do not write mock rows. Live UI metrics still use
the development mock payload.
