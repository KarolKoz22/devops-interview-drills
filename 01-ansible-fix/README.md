# Task 1 — Fix the broken Ansible playbook

**Time budget: 15–20 minutes.** Set a timer.

## Scenario

You've inherited `playbook.yml`. It's meant to install nginx, deploy a
site config from a template, enable the site, remove the default site,
and restart nginx when the config changes. A colleague complains that
running it in CI as a drift-check always reports changes (or fails
outright) even on a box it already configured.

## Your task

1. Read `playbook.yml` and `files/nginx.conf.j2`.
2. Run it against the practice container (see Setup below) and see what
   actually happens — don't just review, execute.
3. Fix the playbook so that:
   - The first run succeeds and nginx ends up actually serving the
     rendered config (not literal `{{ inventory_hostname }}` text).
   - A **second, immediate rerun** reports `changed=0` for every task.
4. Be ready to explain, out loud, *why* each original task was wrong —
   that's the part an interviewer actually cares about, not just the diff.

## Setup

```bash
./setup.sh
ansible-playbook -i inventory.ini playbook.yml   # run 1 — watch it fail/misbehave
ansible-playbook -i inventory.ini playbook.yml   # run 2 — still not idempotent
```

Edit `playbook.yml` in place, rerun both commands until run 2 is clean.

Useful commands while debugging, run from inside the container:

```bash
docker exec practice-ansible cat /etc/nginx/sites-available/app.conf
docker exec practice-ansible nginx -t
docker exec practice-ansible systemctl status nginx
```

## Cleanup

```bash
./cleanup.sh
```

## When you're done

Compare against `SOLUTION.md`. It also lists every bug by name in case you
get stuck and want a hint instead of the full answer — try covering the
fixed playbook and reading just the bug list first.
