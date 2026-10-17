# Incident 02: Website returns 502 after a proxy configuration change

**Simulation only.** Work in the repository root. Start from a clean baseline;
reset clears temporary notes and injected failures. Open a ticket before injecting.

## Customer report
> The website broke after a configuration update.

Ask when it started, which action fails, whether everyone is affected, and whether
anything changed. Request timestamps and error details without collecting secrets.

## Reproduce
```bash
bash scripts/lab.sh reset
bash scripts/lab.sh inject wrong-port
python3 scripts/verify.py wrong-port
```
Expected: GET / returns 502, while the app health check remains healthy.
`PASS` here means the expected failure was reproduced, not that service is healthy.
For this scenario, health alone is not an adequate recovery test.

## Investigate
Save evidence before resetting or repairing:
```bash
docker compose ps
docker compose exec -T proxy nginx -T
docker compose exec -T app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').status)"
docker compose logs --tail=40 proxy
```
Compare proxy_pass port 8999 with the application listener on 8000. Syntax validation passes because the configuration is valid Nginx syntax; it does not verify upstream reachability.

## Root cause and targeted recovery
The upstream port is incorrect. The application itself is healthy.
```bash
cp nginx/healthy.conf nginx/default.conf
docker compose exec -T proxy nginx -t
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
Review configuration diffs and add a through-proxy smoke test after changes.

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
