import json
import subprocess
import sys

CONTEXT="kubeadm-homelab"

def kubectl_json(*args):
    result=subprocess.run(["kubectl", "--context", CONTEXT, *args, "-o", "json"], capture_output=True, text=True)
    if result.returncode!=0:
        print(f"kubectl {' '.join(args)} failed")
        sys.exit(1)
    return json.loads(result.stdout)

pods=kubectl_json("get", "pods", "-n", "monitoring")
print(type(pods))