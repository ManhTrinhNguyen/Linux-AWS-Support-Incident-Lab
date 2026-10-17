# Linux & AWS Support Incident Lab

Practice investigating a user's problem, finding the cause, restoring service,
and explaining the result. This is a technical support portfolio project built
around a Python application, Nginx, Linux permissions, storage, and optional AWS.
All incidents are simulations. No professional experience or completed incidents
are implied by downloading this repository.

## What you will learn
- Tell two different HTTP 502 causes apart using evidence.
- Investigate permission errors, full storage, and HTTP 504 timeouts.
- Recognize that a healthy process can still fail a user's workflow.
- Write support tickets, customer updates, knowledge-base articles, and escalations.
- Optionally troubleshoot systemd, EC2 connectivity, and IAM/S3 access.

## How it works
Your browser sends a request to Nginx on localhost:8080. Nginx forwards it to the
Python application on port 8000 inside a private Docker network. The application
writes fixed test notes to a temporary 1 MiB filesystem. Nothing uses a real customer
database. Request IDs connect application errors with responses.

| Component | Purpose |
|---|---|
| Nginx | Reverse proxy; produces gateway errors when the backend cannot respond |
| Python app | Homepage, /health, and POST /notes endpoints |
| /data tmpfs | Small temporary storage used for safe storage/permission exercises |
| /control tmpfs | Temporary marker used to simulate a slow request |
| scripts/ | Start, inject, reset, and verify scenarios |
| docs/incidents/ | Guided diagnosis and targeted recovery |
| templates/ | Blank tickets and knowledge-base article format |
| aws/ | Optional Terraform environment and AWS incident guides |

## 1. Install the prerequisites
On macOS or Windows, install Docker Desktop and start it. On Linux, install Docker
Engine and the Compose plugin. You also need Git, Python 3, curl, and Bash.
On Windows use WSL2 or Git Bash for the shell examples.

Verify in your terminal:
```bash
docker version
docker compose version
python3 --version
```
Use Docker Compose v2 with `--wait` support. Docker must be running, not merely installed.
The first build needs network access to download the Python and Nginx images.

## 2. Open the repository
After downloading the ZIP, unzip it and open a terminal inside the
`linux-aws-support-incident-lab` folder. You should see compose.yaml and README.md.
If you have already published the repository, you can instead clone your own URL:
```bash
git clone https://github.com/YOUR_USERNAME/linux-aws-support-incident-lab.git
cd linux-aws-support-incident-lab
```
Replace YOUR_USERNAME with your GitHub name. This URL is a placeholder.

## 3. Start a healthy application
```bash
bash scripts/lab.sh start
python3 scripts/verify.py healthy
python3 scripts/verify.py write-ok
```
Expected: `PASS healthy: HTTP 200` and `PASS write-ok: HTTP 201`.
Visit http://127.0.0.1:8080/ in your browser. A small JSON response is normal;
this project focuses on troubleshooting rather than frontend design.

Try the requests manually:
```bash
curl -i http://127.0.0.1:8080/health
curl -i -X POST http://127.0.0.1:8080/notes
```
Notes and control files are temporary and disappear when containers are recreated.
This application is for a private lab, not production hosting.

## 4. Complete first incident
Copy templates/ticket.md to evidence/LAB-001.md. Then:
```bash
bash scripts/lab.sh inject stopped-backend
curl --max-time 8 -i http://127.0.0.1:8080/
docker compose ps -a
docker compose logs --tail=40 proxy
```
You should see HTTP 502. Before resetting, explain why it happened in your ticket.
Follow [incident 01](docs/incidents/01-stopped-backend.md) for recovery and validation.
Record your actual observations; do not copy sample evidence.

## 5. Work through the remaining cases
Start each case with a reset. Inject only one failure at a time.

| Incident | Inject argument | What fails | Guide |
|---|---|---|---|
| 01 | stopped-backend | Homepage: 502 | [Stopped backend](docs/incidents/01-stopped-backend.md) |
| 02 | wrong-port | Homepage: 502; app is healthy | [Wrong upstream port](docs/incidents/02-wrong-port.md) |
| 03 | permissions | Saving: 500 | [Write permissions](docs/incidents/03-permissions.md) |
| 04 | disk-full | Saving: 500 | [Full storage](docs/incidents/04-disk-full.md) |
| 05 | timeout | Homepage: 504; health works | [Slow backend](docs/incidents/05-timeout.md) |

Example:
```bash
bash scripts/lab.sh reset
bash scripts/lab.sh inject permissions
python3 scripts/verify.py permissions
```
Here `PASS permissions` means the expected FAILURE was reproduced.
To restore a completely clean baseline:
```bash
bash scripts/lab.sh reset
python3 scripts/verify.py healthy
python3 scripts/verify.py write-ok
```
A reset is a convenience, not a diagnosis. Use the targeted recovery in each guide
and verify the original failed action before closing your ticket.

## 6. Add AWS and native Linux practice
After completing the local cases:
- [AWS deployment, security groups, and IAM/S3](aws/README.md)
- [Native systemd service failure](docs/native-linux.md)

AWS is optional and billable. Review the Terraform plan before applying, and destroy
the environment when finished. The default local lab creates no AWS resources.
If adapting your existing Terraform project, use a separate sandbox instance and
security group; reuse the runbooks without running fault commands against other workloads.


## Tests
No third-party Python packages are required:
```bash
python3 -m unittest discover -s tests -v
```
Full Docker scenario/recovery suite (recreates this lab's temporary data):
```bash
bash scripts/smoke.sh
```
GitHub Actions runs both checks on push and pull request. It does not deploy AWS.
See [validation status](docs/validation.md) for what was and was not run during creation.

## Useful commands
```bash
bash scripts/lab.sh status
bash scripts/lab.sh logs
bash scripts/lab.sh reset
bash scripts/lab.sh stop
```
If port 8080 is in use, stop the other application or change the host port in
compose.yaml. If changed to 8081, use `python3 scripts/verify.py healthy --base
http://127.0.0.1:8081` on one line and update curl/browser URLs. The smoke script
assumes 8080. If the app fails to start, inspect `docker compose logs app`.
If Docker is not reachable, start Docker Desktop or check daemon permissions.

