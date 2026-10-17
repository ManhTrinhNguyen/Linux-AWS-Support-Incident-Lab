# Incident 05: Application request times out while health remains green

**Simulation only.** Work in the repository root. Start from a clean baseline;
reset clears temporary notes and injected failures. Open a ticket before injecting.

## Customer report
> The website waits and then shows a gateway timeout.

Ask when it started, which action fails, whether everyone is affected, and whether
anything changed. Request timestamps and error details without collecting secrets.

## Reproduce
```bash
bash scripts/lab.sh reset
bash scripts/lab.sh inject timeout
python3 scripts/verify.py timeout
```
Expected: GET / returns 504 after roughly two seconds, while GET /health returns 200.
`PASS` here means the expected failure was reproduced, not that service is healthy.
For this scenario, health alone is not an adequate recovery test.

## Investigate
Save evidence before resetting or repairing:
```bash
docker compose exec -T proxy nginx -T
docker compose logs --tail=40 proxy
docker compose exec -T app ls -l /control
curl --max-time 8 -i http://127.0.0.1:8080/health
```
The /control/slow marker makes homepage handling take five seconds. Nginx proxy_read_timeout is two seconds. A healthy process is not proof that all routes meet response-time requirements.

## Root cause and targeted recovery
The deliberately injected backend delay exceeds the proxy read timeout.
```bash
docker compose exec -T app rm /control/slow
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
Measure endpoint latency and investigate slow work. Increasing a timeout alone can mask the underlying issue.

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
