# Turn completed practice into accurate resume evidence

Keep this under Projects, not Employment. Only use a claim after you can reproduce
it and explain each step. These are suggested bullet structures, not completed work:

- Built a Linux support lab with Nginx and a Python service; reproduced and resolved
  [actual number] simulated incidents involving [the scenarios you completed].
- Diagnosed failures using container state, application/proxy logs, HTTP responses,
  filesystem permissions, and storage utilization; documented recovery verification.
- Created [actual number] simulated support tickets and [actual number] knowledge-base
  articles covering reproduction, root cause, customer updates, and escalation.

Only after the AWS exercises are completed:
- Deployed a disposable AWS support environment with Terraform and investigated
  security-group connectivity and IAM/S3 access behavior using least-privilege checks.

Only after the systemd exercise is completed:
- Investigated a failed Linux service with systemctl and journalctl, corrected its
  ExecStart configuration, and verified HTTP recovery.

Do not claim production operations, real customer incidents, achieved SLAs, reduced
MTTR, or cost savings from lab work. If you measure a lab result, state the method
and label it as a lab measurement.

For your technical support resume, put this project near the top alongside your
API/SQL lab and Python monitoring work. Shorten deployment-only bullets to make room.
Practice answering: What evidence distinguished the two 502 incidents? Why did a
healthy /health endpoint not catch failed writes? Why was chmod 777 unnecessary?
