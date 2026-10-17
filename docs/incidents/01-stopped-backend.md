# Incident 01: Website returns 502 after a service interruption

**Simulation only.** Work in the repository root. Start from a clean baseline;
reset clears temporary notes and injected failures. Open a ticket before injecting.

## Customer report
> The homepage is unavailable.

Ask when it started, which action fails, whether everyone is affected, and whether
anything changed. Request timestamps and error details without collecting secrets.

## Reproduce
```bash
bash scripts/lab.sh reset
bash scripts/lab.sh inject stopped-backend
python3 scripts/verify.py stopped-backend
```
Expected: GET / returns 502. The backend container is stopped.
`PASS` here means the expected failure was reproduced, not that service is healthy.
For this scenario, health alone is not an adequate recovery test.

## Investigate
Save evidence before resetting or repairing:
```bash
docker compose ps -a
docker compose logs --tail=40 proxy
docker compose logs --tail=40 app
```
The proxy is running, but it cannot establish a connection to the application. Compare container state with proxy connection errors. A 502 alone does not prove why the upstream is unavailable.

## Root cause and targeted recovery
The lab deliberately stopped the backend. In a real case, investigate the exit reason and preceding events before deciding whether a restart is sufficient.
```bash
docker compose start app
docker compose exec -T app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').status)"
docker compose exec -T proxy nginx -s reload
```
After a proxy reload or backend start, allow a few seconds for readiness and retry
verification if necessary. A transient failure is not a confirmed recovery.

## Verify recovery
```bash
python3 scripts/verify.py healthy
python3 scripts/verify.py write-ok
curl --max-time 8 -i http://127.0.0.1:8080/
```
Expect 200 health, 201 write, and 200 homepage. For the timeout exercise, confirm
homepage latency also returns to normal. Compare with the original customer action.

## Prevent recurrence
Add backend availability monitoring and document an approved recovery procedure. Identify what stopped the process before choosing a restart policy.

## Finish your ticket
Record your real timestamps, commands, observed output, competing hypotheses,
verified cause, customer update, and verification. Use
[the template](../../templates/ticket.md). The cause above is an exercise answer,
not evidence that you performed the investigation. If the symptoms differ, stop and
investigate instead of copying the expected result.

## Full reset
```bash
bash scripts/lab.sh reset
```
