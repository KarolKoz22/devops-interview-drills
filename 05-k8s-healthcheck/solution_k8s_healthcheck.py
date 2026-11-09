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
