# Task 2 — Convert a Compose file to a Swarm stack

**Time budget: 15–20 minutes.**

## Scenario

`docker-compose.yml` runs two services locally with `docker compose up`
just fine: a custom-built `web` (nginx serving `web/index.html`) in front
of an `api` (a tiny echo server). Now you're asked to run the same two
services on Docker Swarm instead — a `docker stack deploy`, not
`docker compose up`.

## Your task

1. Try deploying the file as-is (see Setup) and read the error.
2. Produce a `docker-stack.yml` that:
   - Actually deploys successfully with `docker stack deploy -c docker-stack.yml practice`
   - Runs `web` with 2 replicas
   - Restarts either service automatically if a task dies
   - Still lets `web` reach `api` by name (there's no `links:` in Swarm —
     figure out what replaces it)
3. Scale `web` to 3 replicas live, without editing the file
   (`docker service scale ...`).
4. Do a rolling update: change something in `web/index.html`, rebuild the
   image under a new tag, and roll it out with `docker service update
   --image ...`. Watch `docker service ps practice_web` show the old
   tasks being replaced one at a time.

## Setup

```bash
docker swarm init --advertise-addr 127.0.0.1   # single-node swarm, local only
docker stack deploy -c docker-compose.yml practice   # step 1 — watch it fail
```

Useful commands while you work:

```bash
docker service ls
docker stack ps practice
docker service logs practice_web --tail 20
docker service update --image <new-tag> practice_web
```

**Note on reachability:** in some nested/virtualized environments the
Swarm routing mesh (the `*:8080->80/tcp` published port) can be flaky
even when everything is actually healthy — if `curl localhost:8080`
hangs, don't assume your stack file is wrong. Check `docker service ps`
and `docker service logs` first; if replicas are `Running` and logs look
clean, the deploy is correct regardless of the curl behavior.

## Cleanup

```bash
docker stack rm practice
docker swarm leave --force
docker rmi practice-web:latest practice-web:v2 2>/dev/null || true
```

## When you're done

Compare against `SOLUTION.md` — it also has a by-name list of what had to
change and why, in case you want a hint before the full file.
