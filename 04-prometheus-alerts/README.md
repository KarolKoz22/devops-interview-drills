# Task 4 — Write Prometheus alerting rules

**Time budget: 10 minutes.**

## Scenario

You're adding alerting on top of an existing Prometheus + node_exporter
setup (exactly the "Dodanie funkcji monitorowania i alarmowania" line in
the JD). `starter-rules.yml` has the two alerts you need, stubbed with
`TODO`s.

## Your task

Fill in `starter-rules.yml` so that:

1. **`HighDiskUsage`** fires when a filesystem is over 85% used,
   *sustained for 5 minutes* (not a single spike). Available metrics:
   `node_filesystem_avail_bytes` and `node_filesystem_size_bytes`, both
   labeled by `instance`, `mountpoint`, `fstype` — exclude `fstype`
   values `tmpfs` and `overlay`, they're not real disks. `severity:
   warning`. The annotation should mention which host and mountpoint,
   using the label/value template variables, not a static string.

2. **`InstanceDown`** fires when a target has been unreachable for 2
   minutes. Available metric: `up` (`1` = healthy scrape, `0` = failed),
   labeled by `instance` and `job`. `severity: critical`.

## Validate it

You don't need a running Prometheus to check syntax — `promtool` is
bundled in the official image:

```bash
docker run --rm --entrypoint promtool \
  -v "$PWD/starter-rules.yml:/rules.yml" \
  prom/prometheus:latest check rules /rules.yml
```

The starter file fails right now (`not a valid duration string: "TODO"`)
— get it to `SUCCESS: 2 rules found`.

## When you're done

Compare against `SOLUTION.md` — also has a couple of talking points worth
raising unprompted if the interview goes conceptual (alert fatigue,
`for:`, why exclude tmpfs/overlay).
