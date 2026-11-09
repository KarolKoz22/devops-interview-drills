# Task 3 — Write a log/alerting script

**Time budget: 10–15 minutes.** Pick Bash or Python — the JD accepts either.

## Scenario

You're asked to add a simple health check that could be wired into cron
or a monitoring system's script check: scan an application log for
recent errors and decide whether to alert.

`sample.log` contains timestamped lines like:

```
2026-08-27T10:14:02 INFO  request completed in 42ms
2026-08-27T10:14:05 ERROR db connection timeout
2026-08-27T10:14:09 WARN  slow query 1200ms
```

## Your task

Write a script (`check_errors.sh` or `check_errors.py`) that:

1. Takes a log file path as its first argument.
2. Counts lines at `ERROR` level (or above — treat `CRITICAL` the same)
   within the **last 5 minutes** relative to the newest timestamp in the
   file (not wall-clock "now" — the sample log is static, so anchor to
   its own last entry, exactly like you'd anchor to "now" in production).
3. Prints a one-line summary, e.g. `3 error(s) in the last 5 minutes`.
4. Exits with status `0` if the count is below a threshold (default: 3),
   and status `1` (with the summary printed to stderr) if at or above it
   — the kind of exit code a monitoring check (Icinga2, a cron job, a
   Nagios-style plugin) actually keys off of.
5. Threshold should be overridable via a second argument or an env var —
   your choice, just be consistent and mention which you picked.

Bonus if you have time: also print the actual matching lines when
alerting, so whoever gets paged has context without a second command.

## Test it

```bash
chmod +x check_errors.sh
./check_errors.sh sample.log        # should exit 1 — sample.log is built to trip the default threshold
echo $?
./check_errors.sh sample.log 100    # should exit 0 with a high threshold
echo $?
```

## When you're done

Compare against `SOLUTION.md` (both a Bash and a Python reference version
are included — worth reading whichever one you *didn't* write, since
you'll likely be asked "could you also do this in Python/Bash?" live).
