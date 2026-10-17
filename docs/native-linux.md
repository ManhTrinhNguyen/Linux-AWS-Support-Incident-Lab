# Native Linux service failure (optional)

Use a disposable Linux VM with systemd, or the EC2 lab. These commands do not run
on macOS directly. This service is separate from Docker and listens only on loopback.
It serves an empty lab directory, never your home directory.

```bash
sudo install -d -m 755 /opt/support-lab-native
sudo tee /etc/systemd/system/support-lab-native.service >/dev/null <<'EOF'
[Unit]
Description=Support incident lab native HTTP service
After=network.target
[Service]
User=nobody
Group=nobody
WorkingDirectory=/opt/support-lab-native
ExecStart=/usr/bin/python3 -m http.server 8090 --bind 127.0.0.1
Restart=no
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
[Install]
WantedBy=multi-user.target
EOF
```
On Ubuntu, change `Group=nobody` to `Group=nogroup` if `getent group nobody`
returns nothing. On Amazon Linux, verify both with `getent passwd nobody` and
`getent group nobody`. Verify `/usr/bin/python3 --version` before starting.

```bash
sudo systemctl daemon-reload
sudo systemctl start support-lab-native
curl -i http://127.0.0.1:8090/
```

Inject an invalid executable path through a dedicated drop-in:
```bash
sudo mkdir -p /etc/systemd/system/support-lab-native.service.d
sudo tee /etc/systemd/system/support-lab-native.service.d/incident.conf >/dev/null <<'EOF'
[Service]
ExecStart=
ExecStart=/missing-lab-python -m http.server 8090 --bind 127.0.0.1
EOF
sudo systemctl daemon-reload
sudo systemctl restart support-lab-native
```
The last command is expected to fail. Investigate before reading the recovery:
```bash
sudo systemctl status support-lab-native --no-pager
sudo journalctl -u support-lab-native -n 30 --no-pager
sudo systemctl cat support-lab-native
sudo ss -ltnp
```
Expected evidence: failed process execution, commonly status=203/EXEC, with a
nonexistent ExecStart path. A blind restart cannot repair this configuration.

Recovery:
```bash
sudo rm /etc/systemd/system/support-lab-native.service.d/incident.conf
sudo systemctl daemon-reload
sudo systemctl reset-failed support-lab-native
sudo systemctl start support-lab-native
curl -i http://127.0.0.1:8090/
```
Cleanup:
```bash
sudo systemctl stop support-lab-native
sudo rm /etc/systemd/system/support-lab-native.service
sudo rmdir /etc/systemd/system/support-lab-native.service.d
sudo systemctl daemon-reload
sudo rmdir /opt/support-lab-native
```
Save your own sanitized evidence and explain why configuration validation would
help prevent recurrence. No native service uptime or customer impact is implied.
