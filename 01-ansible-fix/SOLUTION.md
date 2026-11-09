# Solution — Task 1

Verified: run 1 → `changed=6`, run 2 → `changed=0`, `nginx -t` passes,
`systemctl is-active nginx` → `active`.

## The bugs, one per original task

1. **`shell: apt-get update && apt-get install -y nginx`** — `shell`
   always reports `changed`, and re-running `apt-get install` on an
   already-installed package is silently wasted work. Fix: the `apt`
   module with `state: present` (idempotent — only installs if missing)
   and `update_cache: true` (still refreshes the index, but the *task*
   only reports changed when a package actually gets installed).

2. **`copy: src: files/nginx.conf.j2`** — this is the one that actually
   broke things: `copy` moves the file byte-for-byte, so
   `{{ inventory_hostname }}` was written to disk *literally*, and nginx
   refused to start because unrendered `{{ }}` isn't valid config syntax.
   Fix: the `template` module, which runs the file through Jinja2 before
   writing it.

3. **`shell: ln -s ...`** — works once, then fails on every subsequent run
   with "File exists" because `ln -s` has no built-in "only if missing"
   behavior. Fix: `file: state: link` — idempotent, only (re)creates the
   symlink if it doesn't already point at the right target.

4. **`shell: rm -f ...`** — same category of problem: always reports
   `changed` via `shell`, even when the file was already gone. Fix:
   `file: state: absent` — reports `changed` only the first time it
   actually removes something.

5. **`shell: systemctl restart nginx`** — runs unconditionally on *every*
   playbook run, which is exactly the "always changed" symptom the
   colleague complained about, and also masks whether nginx was already
   fine. Fix: two changes — (a) move the restart into a `handler`,
   `notify`'d only by the tasks that actually change config (`template`,
   the symlink, the default-site removal); (b) add a separate task using
   the `systemd` module with `enabled: true, state: started` to guarantee
   nginx is running and boots on startup — that one *is* idempotent and
   safe to run unconditionally, unlike a raw restart.

## Fixed playbook

```yaml
---
- name: Configure nginx reverse proxy
  hosts: practice
  become: true
  handlers:
    - name: restart nginx
      systemd:
        name: nginx
        state: restarted
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
        update_cache: true

    - name: Deploy site config
      template:
        src: files/nginx.conf.j2
        dest: /etc/nginx/sites-available/app.conf
      notify: restart nginx

    - name: Enable site
      file:
        src: /etc/nginx/sites-available/app.conf
        dest: /etc/nginx/sites-enabled/app.conf
        state: link
      notify: restart nginx

    - name: Remove default site
      file:
        path: /etc/nginx/sites-enabled/default
        state: absent
      notify: restart nginx

    - name: Ensure nginx is enabled and running
      systemd:
        name: nginx
        enabled: true
        state: started
```

## If you want to go further

- Add a task that runs `nginx -t` (via the `command` module,
  `changed_when: false`) before the restart handler, so a bad template
  fails loudly with a clear message instead of leaving nginx crash-looped.
- Talk through: why is `notify` + handler better than a plain
  unconditional restart task, specifically in terms of *when* the
  restart actually needs to happen (only after config changes, and only
  once even if three tasks all notify it in the same run — handlers
  dedupe and run at the end of the play).
