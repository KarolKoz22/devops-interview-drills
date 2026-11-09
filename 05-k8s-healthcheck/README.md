# Task 5 — Kubernetes health-check script

**Time budget: 20–25 minutes.** Set a timer.

## Scenario

You're asked, in the interview, to write a small script that could be
dropped into a cron job or monitoring sidecar to check whether a
Kubernetes cluster is healthy — no dashboards, just exit code + a
summary an alert system could parse.

## Your task

Write a script (Bash or Python, your choice — the JD lists both) that:

1. Checks every **node** is `Ready`.
2. Checks every **pod**, across all namespaces, is actually healthy —
   not just "exists". Think about what "healthy" should mean: a pod can
   show up in `kubectl get pods` while still being a problem (stuck
   container, evicted, crash-looping, flapping with high restart counts).
3. Prints a short summary (counts checked / counts flagged).
4. Prints the flagged items with enough detail to act on (namespace,
   pod/node name, what's wrong).
5. **Exits non-zero if anything is flagged, 0 if the cluster is clean** —
   that's what makes it usable by cron/monitoring rather than just a
   human-readable report.

## Setup

This one runs against your real `kubeadm-homelab` cluster — no
disposable container to spin up. Just make sure both VMs are up:

```bash
virsh start k8s-control k8s-worker1   # already running is fine, this is a no-op then
kubectl --context kubeadm-homelab get nodes   # sanity check before you start timing
```

**Use `--context kubeadm-homelab` explicitly wherever you call
`kubectl`** — your `~/.kube/config` has a second, unrelated context
(`default`, a separate k3s cluster on this same laptop) and relying on
whatever the ambient default happens to be has bitten you before on
this project.

Since this script only reads cluster state, it's naturally idempotent —
but be ready to explain *why* that's true if asked, and what would
change if the script also took remediation action (e.g. restarting a
pod) instead of just reporting.

## When you're done

Compare against `SOLUTION.md`. Real output from your actual cluster is
included there — not fabricated — so if your numbers differ, that's
your cluster's state changing between runs, not a wrong answer by
definition; check whether the *reasoning* matches.
