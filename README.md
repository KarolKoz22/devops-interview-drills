# DevOps Interview Practice

Five self-contained drills built from the JD you shared (Ansible/Linux
infra, Docker Swarm containerization, Bash/Python scripting, Prometheus
alerting, Kubernetes health-checking). Every task was actually run and
verified while building this — not hypothetical — so the "expected"
behavior in each README is real.

Each folder has:
- `README.md` — the task + a time budget. Read only this first.
- `SOLUTION.md` — a verified reference answer, plus talking points for
  when the interview goes conceptual. Don't open until you've attempted it.
- `setup.sh` / `cleanup.sh` where a live target is needed.

## Suggested mock-interview flow (60 min)

1. **5 min** — talk through the k8s-kubeadm-setup + ansible project you
   already have at `~/Desktop/homelab/ansible/` — that's real, recent,
   talkable material (two-phase `add_host` provisioning, a shared
   `vm_provision` role, idempotent OS prep). Lead with it if asked "tell
   me about something you've built."
2. **20–25 min** — pick ONE of tasks 01/02, time yourself with a real
   timer, no peeking at SOLUTION.md until you're done or time's up.
3. **10 min** — talk through your solution out loud as if explaining it
   to the interviewer, including what you'd have done differently with
   more time.
4. Repeat with task 03 or 04 if time allows — they're shorter.

## Tasks

| Folder | Mirrors JD line | Time budget |
|---|---|---|
| `01-ansible-fix` | "Konfigurowanie i utrzymywanie... [Linux, Ansible]" | 15–20 min |
| `02-docker-swarm` | "Wsparcie... konteneryzacji [Docker, Docker Swarm]" | 15–20 min |
| `03-bash-script` | "Umiejętności pisania skryptu – Bash lub Python" | 10–15 min |
| `04-prometheus-alerts` | "Dodanie funkcji monitorowania i alarmowania" | 10 min |
| `05-k8s-healthcheck` | "Umiejętności pisania skryptu" + monitoring, applied to real k8s | 20–25 min |

## Cleanup / hygiene

Tasks 01 and 02 spin up real Docker containers/a real single-node Swarm.
Each has its own cleanup, but to check nothing's left running between
sessions:

```bash
docker ps -a --filter "name=practice"
docker service ls          # should error "not a swarm manager" once cleaned up
docker images | grep practice
```

## A couple of things worth rehearsing regardless of which task comes up

- **Idempotency, out loud.** Nearly every real DevOps interview task
  eventually asks "would running this twice cause a problem?" — have an
  instinctive answer, not one you have to derive live.
- **"How would you monitor/alert on this?"** — given the JD's emphasis,
  assume any infra task might get this follow-up even if the task itself
  wasn't about monitoring.
- **English.** The JD asks for good spoken/written English specifically
  — if the interview offers a language choice, doing at least the
  technical explanation part in English is worth doing deliberately, not
  just when asked.
