# Solution — Task 4

Verified: `promtool check rules` reports `SUCCESS: 2 rules found` against
this file.

```yaml
groups:
  - name: infra-alerts
    rules:
      - alert: HighDiskUsage
        expr: (1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes{fstype!~"tmpfs|overlay"})) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High disk usage on {{ $labels.instance }} ({{ $labels.mountpoint }})"
          description: "{{ $labels.mountpoint }} on {{ $labels.instance }} is {{ $value | printf \"%.1f\" }}% full (threshold 85%, for 5m)."

      - alert: InstanceDown
        expr: up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.instance }} is down"
          description: "{{ $labels.job }}/{{ $labels.instance }} has been unreachable for more than 2 minutes."
```

## Why each piece is there (say this part out loud in the interview)

- **`for: 5m` / `for: 2m`** — without `for:`, a one-second metric spike
  pages someone. `for:` requires the condition to stay true across every
  scrape in that window before the alert actually fires — this is *the*
  mechanism for avoiding alert fatigue from noisy, self-correcting
  blips, and interviewers listen for whether you know this exists.
- **`fstype!~"tmpfs|overlay"`** — `tmpfs` is RAM-backed and often near
  "full" by design (it's sized small on purpose); `overlay` is the
  container filesystem layer, not a real disk — both would generate
  false positives on any node running containers.
- **`{{ $labels.instance }}` / `{{ $labels.mountpoint }}` / `{{ $value
  }}`** — Prometheus templates `annotations`/`summary` per firing series,
  so a multi-disk, multi-host alert still tells you exactly *which* host
  and mountpoint without needing to open a dashboard first. A hardcoded
  string here is a common beginner tell.
- **`up == 0`** — `up` is a synthetic metric Prometheus generates itself
  per scrape target (1 = last scrape succeeded, 0 = failed) — no
  exporter needs to expose it, which is why it's the standard way to
  alert on "target unreachable" rather than trying to infer it from
  application metrics.

## If the interview goes conceptual from here

Likely follow-ups and short honest answers:

- **"Where would this alert actually go?"** — Alertmanager, which
  dedupes/groups/routes rules' firing alerts to Slack/email/PagerDuty,
  and can be configured for time-based silencing and severity-based
  routing (e.g., `severity: critical` → pages, `warning` → Slack only).
- **"Why Prometheus `for:` instead of just averaging over time in the
  query itself (`avg_over_time`)?"** — `for:` is simpler and is what the
  UI/API surfaces as "pending → firing" state; `avg_over_time` changes
  what you're actually measuring (a smoothed value) rather than "how long
  has the raw condition held."
- **This JD lists Icinga2 *and* Prometheus/Grafana/InfluxDB** — worth
  asking them directly which one is authoritative for alerting and which
  is legacy/being phased out; shows you noticed the redundancy rather
  than assuming you already know their setup.
