# Incident 03: Application loads but cannot save notes

**Simulation only.** Work in the repository root. Start from a clean baseline;
reset clears temporary notes and injected failures. Open a ticket before injecting.

## Customer report
> I can open the application, but saving fails.

Ask when it started, which action fails, whether everyone is affected, and whether
anything changed. Request timestamps and error details without collecting secrets.

## Reproduce
```bash
bash scripts/lab.sh reset
bash scripts/lab.sh inject permissions
python3 scripts/verify.py permissions
```
Expected: GET /health returns 200, but POST /notes returns 500 with write_failed.
`PASS` here means the expected failure was reproduced, not that service is healthy.
For this scenario, health alone is not an adequate recovery test.

## Investigate
Save evidence before resetting or repairing:
```bash
docker compose exec -T app id
docker compose exec -T app ls -ld /data
docker compose logs --tail=40 app
```
Find errno 13 in application logs. The service runs as UID 10001 and /data has mode 500: the owner can read and traverse it but cannot write.

## Root cause and targeted recovery
The injector removes the temporary note file, then removes directory write access. This prevents creating a replacement note. Directory write permission alone does not control writes to an already existing writable file.
```bash
docker compose exec -T --user 0 app chmod 700 /data
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
Define the expected owner and mode. Validate write access as the service user; do not use chmod 777.

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
