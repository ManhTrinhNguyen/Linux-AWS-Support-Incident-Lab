# Automated replay: permissions

Executed at: 2026-10-17T15:00:28.139313+00:00
Status: Failure reproduced; automated recovery checks passed.
Operator: Coding assistant. This is generated execution evidence, not a record of
Trinh independently diagnosing an incident. No real customer was affected.
Environment: Local Linux Python HTTP service and Python reverse proxy.
Docker, Nginx, systemd and AWS were not exercised in this run.

## Baseline
Health, note write, and homepage returned HTTP 200, 201, and 200.

## Injection
Set actual local data-directory mode to 0500.

## Observed failure
```json
{
  "status": 500,
  "body": "{\"error\": \"write_failed\", \"request_id\": \"6e4a4b5c-cd7f-4672-9f64-b29ab9635869\"}",
  "elapsed_seconds": 0.001
}
```

## Recovery
Restore owner write permission with mode 0700.

## Observed recovery
```json
[
  {
    "status": 200,
    "body": "{\"status\": \"ok\", \"request_id\": \"78cf63c0-bdf1-4f09-b89b-abba3d2db035\"}",
    "elapsed_seconds": 0.001
  },
  {
    "status": 201,
    "body": "{\"status\": \"saved\", \"request_id\": \"06968c6d-e45c-496a-8548-c960095bc2b8\"}",
    "elapsed_seconds": 0.001
  },
  {
    "status": 200,
    "body": "{\"service\": \"support-incident-lab\", \"request_id\": \"7ef79ed4-6245-4047-9077-7e51b60bfb97\"}",
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
