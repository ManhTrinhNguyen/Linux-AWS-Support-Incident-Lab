# Application loads but cannot create a note

Applies to: the local support lab.

If /health returns 200 but POST /notes returns HTTP 500 with write_failed,
inspect the matching application log request ID. Errno 13 indicates an access
permission failure; it does not by itself prove which path or permission is wrong.

Check the service identity, directory ownership/mode, and existing file ownership/mode.
Creating a file needs directory write and execute permission. Appending to an
existing file needs write access to that file; changing only directory write access
may not block that operation. This distinction was confirmed while testing this lab.

For the documented lab fault, restore /data to mode 0700 using the targeted recovery
in incident 03. Avoid chmod 777. Repeat POST /notes and require HTTP 201, then verify
health and homepage responses. If errno 13 persists, inspect parent-directory access,
mount flags and security policy before escalating with sanitized logs and commands.

Validation scope: assistant-executed local replay on 2026-10-17. The Docker injector
was corrected but could not be executed here because Docker is unavailable.
