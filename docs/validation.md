# Validation status

During repository creation:
- Python HTTP integration tests: all 5 passed on 2026-10-17 (Python 3.12.14).
- Bash syntax, Python compilation, Compose YAML parsing, and Markdown links:
  all passed during packaging. Terraform HCL/provider validation remains unrun.
- Docker/Nginx full integration: not executed in the authoring environment because
  Docker was unavailable. Run `bash scripts/smoke.sh` or the included GitHub workflow.
- Terraform formatting/validation and AWS deployment: not executed; Terraform and
  AWS credentials were unavailable. Run the documented checks in your sandbox.
- Native systemd exercise: not executed in the authoring environment.

Python tests exercise actual HTTP requests but mock storage errors to make them
portable. The Docker smoke test instead induces real permission and bounded tmpfs
storage failures. Neither a workflow file nor test code is evidence of a passing run.

Images and GitHub Actions use version tags. They can change over time; after a
successful run, record image digests or pin them if you need identical future builds.

## Additional execution on 2026-10-17
All five portable replay cases passed with real HTTP requests and recovery checks.
Actual stopped-server and wrong-port connection failures produced 502; actual
filesystem permissions produced 500; /dev/full produced ENOSPC and 500; an actual
five-second handler delay produced 504 through a Python proxy with a 0.7-second timeout.
Every case recovered to health=200, write=201, and homepage=200.
The permissions injector was corrected to remove its temporary note file before
restricting directory writes. Docker validation of that correction remains unrun.
See evidence/automated-replay/ for raw JSON, reports, and execution output.
