# Automated replay: wrong-port

Executed at: 2026-10-17T15:00:28.129875+00:00
Status: Failure reproduced; automated recovery checks passed.
Operator: Coding assistant. This is generated execution evidence, not a record of
Trinh independently diagnosing an incident. No real customer was affected.
Environment: Local Linux Python HTTP service and Python reverse proxy.
Docker, Nginx, systemd and AWS were not exercised in this run.

## Baseline
Health, note write, and homepage returned HTTP 200, 201, and 200.

## Injection
Point Python proxy at a bound, non-listening port.

## Observed failure
```json
{
  "status": 502,
  "body": "portable proxy: upstream connection failed",
  "elapsed_seconds": 0.001
}
```

## Recovery
Restore the proxy target to the actual backend listener.

## Observed recovery
```json
[
  {
    "status": 200,
    "body": "{\"status\": \"ok\", \"request_id\": \"ae4b3d1d-ea60-4816-bc34-ec1b80e2503d\"}",
    "elapsed_seconds": 0.001
  },
  {
    "status": 201,
    "body": "{\"status\": \"saved\", \"request_id\": \"c68d57a4-5b38-46f6-8306-2ef1388fceac\"}",
    "elapsed_seconds": 0.001
  },
  {
    "status": 200,
    "body": "{\"service\": \"support-incident-lab\", \"request_id\": \"f98cd82e-20e3-4cff-b6a9-583a3bbc9d87\"}",
    "elapsed_seconds": 0.001
  }
]
```

## Interpretation
The scripted mutation produced the expected observable failure and reversing it
restored the original user actions. This validates the tested mechanism, not
independent human root-cause diagnosis or a production operating environment.

## Example customer update
In this simulated environment, we reproduced the reported failure, reversed the
injected fault, and confirmed page loading and saving work again.
