# Solution — Task 2

Verified end-to-end: raw `docker-compose.yml` fails stack deploy with
`unsupported Compose file version: 2.4`; the fixed file below deployed
both services (`practice_api 1/1`, `practice_web 2/2`), scaled to 3/3
cleanly, and a `--image` rolling update converged with old tasks replaced
one at a time.

## What had to change, and why

1. **`version: '2.4'` → `'3.8'`** — `docker stack deploy` only understands
   Compose spec v3+; the `deploy:` key (replicas, restart policy,
   resources) doesn't exist at all in v2. This is the error you hit
   immediately trying the raw file.

2. **`build: ./web` → `image: practice-web:latest`** — Swarm has no build
   step; every node that might run a task needs to be able to *pull* the
   image, not build it. In practice: `docker build -t practice-web:latest
   ./web` first, then reference the tag. (On a real multi-node swarm
   you'd push it to a registry too — on this single-node practice setup
   the locally built image is enough.)

3. **`container_name: web` → removed** — Swarm assigns names itself based
   on service name + replica index (`practice_web.1`, `practice_web.2`,
   ...); a fixed name can't work once there's more than one replica.

4. **`links: - api` → removed, relies on the overlay network's embedded
   DNS** — `links` is a legacy standalone-Docker feature, silently
   ignored in Swarm mode. `docker stack deploy` auto-creates an overlay
   network per stack (`practice_default` here) and every service is
   reachable by its service name on it — `web` can just resolve `api`
   without any explicit link.

5. **`restart: always` → `deploy.restart_policy.condition: any`** — the
   plain Compose `restart:` key is ignored by the Swarm scheduler; restart
   behavior for a service belongs under `deploy:`.

6. **No `deploy:` section → added `replicas` and `restart_policy`** —
   this is what actually gives you the "2 replicas of web" requirement
   and the "restart on failure" behavior.

## Fixed `docker-stack.yml`

```yaml
version: '3.8'
services:
  web:
    image: practice-web:latest
    ports:
      - "8080:80"
    deploy:
      replicas: 2
      restart_policy:
        condition: any

  api:
    image: hashicorp/http-echo:1.0
    command: ["-text=hello from api", "-listen=:5000"]
    deploy:
      replicas: 1
      restart_policy:
        condition: any
```

```bash
docker build -t practice-web:latest ./web
docker stack deploy -c docker-stack.yml practice
docker service scale practice_web=3
```

## Rolling update — the gotcha I actually hit while verifying this

My first attempt used `docker service update --args '-text=hello v2
-listen=:5000' practice_api` — this failed with `task: non-zero exit
(127)`, because `--args` takes the argv list, and passing one
space-separated string as a single `--args` value doesn't split it the
way you'd expect; the container ends up trying to exec a garbled
argument as if it were the binary. If asked to update just the args of a
running service, the safe form is one `--args` flag per argument:
`--args "-text=hello v2" --args "-listen=:5000"` — or just don't
Google-guess it live, say "let me check the exact flag syntax" rather
than fumbling it in front of an interviewer.

Recovered with `docker service update --rollback practice_api`, which is
itself worth mentioning unprompted — Swarm keeps the previous spec and a
rollback is one command, no redeploy needed.

The **image-based** rolling update is cleaner and more representative of
real usage:

```bash
# edit web/index.html, then:
docker build -t practice-web:v2 ./web
docker service update --image practice-web:v2 practice_web
docker service ps practice_web   # watch tasks get replaced one at a time
```

## If asked "why not just use Kubernetes"

Have a one-line answer ready: Swarm is simpler to operate for a small
team / single-purpose cluster (no separate control plane components, one
binary, `docker stack deploy` reuses Compose syntax); Kubernetes wins on
ecosystem, RBAC, autoscaling, and multi-tenant complexity. Given the JD
lists Swarm specifically (not Kubernetes), they likely run Swarm
precisely because it's "enough" for their scale — don't volunteer that
Kubernetes is objectively better unless asked, it can read as dismissing
their actual stack.
