# Installation, updates and rollback

## Requirements

- Paperless-ngx with the `paperless_ngx.parsers` entry point (validated on `3.3.0`).
- Python `>=3.12` in the environment running the Paperless consumer / worker processes.
- Installed Paperless runtime dependencies; no standalone PDF renderer is supplied by this extension.

## Build from this repository

```bash
python -m pip install build
python -m build
```

The built wheel is produced under `dist/`. Exact filename depends on version.

## community-scripts Proxmox LXC + uv

**Reference layout only** (verify paths and services first):

```bash
# Run in the LXC, after backing up your environment and transferring the wheel.
uv pip install --python /opt/paperless/.venv/bin/python --no-deps /tmp/<wheel-file>.whl
```

Using `--no-deps` avoids touching Paperless's pinned dependencies. Restart only the actual Paperless services that load parser plugins, e.g. consumer, worker and web server. `systemctl` unit names vary; confirm with `systemctl list-units` first.

Validate from the Paperless source directory (the path may differ):

```bash
cd /opt/paperless/src
/opt/paperless/.venv/bin/python -c \
'from paperless.parsers.registry import get_parser_registry; p=get_parser_registry().get_parser_for_file("message/rfc822", "test.eml"); print(p.name, p.version)'
```

## Docker environments

Use an image or persistent initialization strategy that installs the wheel into the same Python environment as Paperless. Do **not** run `pip install` into a disposable running container without a reproducible installation mechanism. The exact approach depends on your Paperless Docker deployment. Restart the Paperless service(s) after rebuilding.

## Updates

Back up the configuration and ensure a rollback wheel is available. Compare release notes with the Paperless version actually installed. Test a representative `.eml` and its attachment processing before promoting to production. Installing a new version does not automatically regenerate existing PDFs.

## Rollback

```bash
uv pip uninstall --python /opt/paperless/.venv/bin/python paperless-ngx-mail-header
```

After uninstalling, restart consumer, workers and web server as applicable and check that `get_parser_for_file("message/rfc822", ...)` selects the built-in parser. No database schema or storage-path changes are made by this package. Old PDFs remain as generated until an explicit reprocessing action.
