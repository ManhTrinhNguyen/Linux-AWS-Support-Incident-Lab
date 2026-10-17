# Automated replay: storage-error

Executed at: 2026-10-17T15:00:28.148360+00:00
Status: Failure reproduced; automated recovery checks passed.
Operator: Coding assistant. This is generated execution evidence, not a record of
Trinh independently diagnosing an incident. No real customer was affected.
Environment: Local Linux Python HTTP service and Python reverse proxy.
Docker, Nginx, systemd and AWS were not exercised in this run.

## Baseline
Health, note write, and homepage returned HTTP 200, 201, and 200.

## Injection
Redirect note writes to Linux /dev/full, which returns real ENOSPC. No filesystem was filled.

## Observed failure
```json
{
  "status": 500,
  "body": "{\"error\": \"storage_full\", \"request_id\": \"fb5f28a9-a793-4a1a-8950-ab084109c917\"}",
  "elapsed_seconds": 0.001
}
```

## Recovery
Remove the device symlink and allow a regular note file to be created.

## Observed recovery
```json
[
  {
    "status": 200,
    "body": "{\"status\": \"ok\", \"request_id\": \"226f65e4-ee28-4897-b235-d8a6f5259495\"}",
    "elapsed_seconds": 0.001
  },
  {
    "status": 201,
    "body": "{\"status\": \"saved\", \"request_id\": \"a2727792-ea0e-4898-8b27-c95ce9c42de6\"}",
    "elapsed_seconds": 0.002
  },
  {
    "status": 200,
    "body": "{\"service\": \"support-incident-lab\", \"request_id\": \"4f1d4b18-08f0-428a-b746-a14dbaf0d91b\"}",
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
