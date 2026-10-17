#!/usr/bin/env bash
set -euxo pipefail
dnf install -y docker git python3 nginx
systemctl enable --now docker
# Compose is installed separately using the official instructions linked in aws/README.md.
# User data deliberately does not fetch or execute this repository automatically.
