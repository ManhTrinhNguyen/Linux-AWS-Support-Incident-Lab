# Incident 04: Saving fails because application storage is full

**Simulation only.** Work in the repository root. Start from a clean baseline;
reset clears temporary notes and injected failures. Open a ticket before injecting.

## Customer report
> Saving a new note returns a server error.

Ask when it started, which action fails, whether everyone is affected, and whether
anything changed. Request timestamps and error details without collecting secrets.

## Reproduce
```bash
bash scripts/lab.sh reset
bash scripts/lab.sh inject disk-full
python3 scripts/verify.py disk-full
```
Expected: POST /notes returns 500 with storage_full; GET /health can still succeed.
`PASS` here means the expected failure was reproduced, not that service is healthy.
For this scenario, health alone is not an adequate recovery test.

## Investigate
Save evidence before resetting or repairing:
```bash
docker compose exec -T app df -h /data
docker compose exec -T app du -h /data
docker compose logs --tail=40 app
```
Find errno 28 and a full /data tmpfs. The exercise fills a capped 1 MiB memory-backed container filesystem, not the host disk.

## Root cause and targeted recovery
A deliberately created filler file consumed the available blocks in the isolated lab filesystem.
```bash
docker compose exec -T app rm /data/filler
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
Monitor storage capacity and application write failures. Use retention or rotation appropriate to the actual data; never remove unknown files just to free space.

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
