# Solution — Task 5

Reference implementation is `solution_k8s_healthcheck.py` (prefixed
`solution_` so it doesn't collide with the script you write). Verified
against the real `kubeadm-homelab` cluster — real output below, not
fabricated.

## The trap in this exercise

`kubectl get pods` output collapses several distinct signals into two
columns (`READY`, `STATUS`), and the raw API object underneath is not
as simple as "phase == Running is good":

- **`Evicted` pods report `status.phase = "Failed"`**, not a phase
  called `"Evicted"` — the human-readable "Evicted" you see in `kubectl
  get pods` actually comes from `status.reason`. If you check phase
  only, you'd correctly flag it as bad, but "Failed" alone doesn't tell
  you *why*, and a good script surfaces the reason. If you check phase
  *and* naively treat every non-`Running` phase as identically bad,
  you'll also flag `Succeeded` (completed Jobs — which is correct
  behavior, not a problem) and miss the fact that a `Running` pod can
  still have an unready container.
- **A pod can be `phase: Running` and still be broken.** The top-level
  phase only reflects "at least one container is running" — the
  per-container `status.containerStatuses[].ready` boolean is what
  actually matters, plus `restartCount` for flapping. This is the part
  most naive solutions miss entirely, because `kubectl get pods`'
  `STATUS` column visually looks authoritative on its own.
- **`Unknown` status happens transiently** whenever a node loses contact
  with the API server (I hit this for real while building this — 12
  pods on `k8s-worker1` went `Unknown` right after restarting
  `k8s-control`, then self-resolved within ~30s once the node
  reconnected). A script run *during* that window isn't wrong to flag
  it — that's real signal — but it's worth knowing it's not always a
  permanent problem, which matters for how you'd tune alert
  debouncing in a real monitoring setup.

## Key design points

- **Always pass `--context kubeadm-homelab` explicitly** — same
  ambient-default-context trap as everywhere else in this project.
- **Exit non-zero on any flagged item, 0 otherwise** — same
  cron/monitoring calling convention as Task 3.
- **Summary to stdout, flagged detail to stderr** — same reasoning as
  Task 3: lets a monitoring system show just the one-liner, full detail
  still available with `2>&1`.
- **Idempotency is free here because it's read-only** — every call is a
  `kubectl get`, no mutation, so running it 100 times in a row changes
  nothing and is always safe. Worth saying this *explicitly* if asked
  the "would running this twice cause a problem?" question, and worth
  contrasting with what would change if the script did remediation
  (e.g. `kubectl delete pod` on a crash-looping pod) instead of just
  reporting — that's no longer trivially idempotent or safe to run
  concurrently, and would need its own locking/rate-limiting story.

## Real verified output

```
$ python3 solution_k8s_healthcheck.py
2 node(s) checked, 0 problem(s)
22 pod(s) checked, 4 problem(s)

--- flagged ---
pod/default/tmp-df3: Evicted
pod/monitoring/cadvisor-8z9lj: Evicted
pod/monitoring/node-exporter-wjppc: Evicted
pod/monitoring/promtail-b5c4m: Evicted
$ echo $?
1
```

All four flagged pods are genuinely stale `Evicted` pods that Kubernetes
doesn't garbage-collect automatically — they linger until deleted
manually (`kubectl delete pod <name> -n <ns>`) or replaced by a
DaemonSet controller, which is exactly the kind of "found a real issue"
result you'd want from this script in production.

## Reference script

```python
#!/usr/bin/env python3
import json
import subprocess
import sys

CONTEXT = "kubeadm-homelab"
RESTART_WARN_THRESHOLD = 5


def kubectl_json(*args):
    result = subprocess.run(
        ["kubectl", "--context", CONTEXT, *args, "-o", "json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.exit(f"kubectl {' '.join(args)} failed: {result.stderr}")
    return json.loads(result.stdout)


def check_nodes():
    problems = []
    nodes = kubectl_json("get", "nodes")["items"]
    for node in nodes:
        name = node["metadata"]["name"]
        conditions = {c["type"]: c["status"] for c in node["status"]["conditions"]}
        if conditions.get("Ready") != "True":
            problems.append(f"node/{name}: NotReady (Ready={conditions.get('Ready')})")
    return len(nodes), problems


def check_pods():
    problems = []
    pods = kubectl_json("get", "pods", "-A")["items"]
    for pod in pods:
        ns = pod["metadata"]["namespace"]
        name = pod["metadata"]["name"]
        phase = pod["status"].get("phase")
        reason = pod["status"].get("reason", "")

        if phase == "Succeeded":
            continue  # completed Jobs are fine

        if reason == "Evicted":
            problems.append(f"pod/{ns}/{name}: Evicted")
            continue

        if phase in ("Failed", "Unknown"):
            problems.append(f"pod/{ns}/{name}: phase={phase}")
            continue

        container_statuses = pod["status"].get("containerStatuses", [])
        for cs in container_statuses:
            if not cs["ready"]:
                waiting = cs["state"].get("waiting", {})
                problems.append(
                    f"pod/{ns}/{name}: container {cs['name']} not ready"
                    + (f" ({waiting['reason']})" if waiting.get("reason") else "")
                )
            if cs["restartCount"] > RESTART_WARN_THRESHOLD:
                problems.append(
                    f"pod/{ns}/{name}: container {cs['name']} restarted {cs['restartCount']}x (flapping)"
                )
    return len(pods), problems


def main():
    node_count, node_problems = check_nodes()
    pod_count, pod_problems = check_pods()
    problems = node_problems + pod_problems

    print(f"{node_count} node(s) checked, {len(node_problems)} problem(s)")
    print(f"{pod_count} pod(s) checked, {len(pod_problems)} problem(s)")

    if problems:
        print("\n--- flagged ---", file=sys.stderr)
        for p in problems:
            print(p, file=sys.stderr)
        sys.exit(1)

    print("cluster healthy")
    sys.exit(0)


if __name__ == "__main__":
    main()
```
