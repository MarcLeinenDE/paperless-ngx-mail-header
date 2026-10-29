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

## GitHub release files

Download the wheel and `SHA256SUMS.txt` from the same [GitHub release](https://github.com/MarcLeinenDE/paperless-ngx-mail-header/releases). Verify the wheel's hash before transferring it to the Paperless environment:

```bash
sha256sum paperless_ngx_mail_header-0.2.0-py3-none-any.whl
# Compare the complete hash with the wheel entry in SHA256SUMS.txt.
```

The project is distributed through GitHub release assets. No PyPI publication is implied.

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

Build a derived image so installation survives container replacement. For the official Paperless `3.3.0` image, whose Dockerfile installs dependencies into system Python, an example is:

```dockerfile
FROM ghcr.io/paperless-ngx/paperless-ngx:3.3.0
COPY paperless_ngx_mail_header-0.2.0-py3-none-any.whl /tmp/
RUN uv pip install --system --no-deps /tmp/paperless_ngx_mail_header-0.2.0-py3-none-any.whl \
    && rm /tmp/paperless_ngx_mail_header-0.2.0-py3-none-any.whl
```

Use the derived image in the services that run the Paperless webserver, consumer and workers. Keep existing volumes, environment variables and mail rules. Rebuild and recreate those services, then verify parser selection as described above. Custom images may use a virtual environment instead; install into their actual interpreter.

The equivalent derived-image installation is exercised in the disposable Docker integration workflow on Paperless `3.3.0`; see [the integration report](integration-report.md). This is not a test of your deployment configuration. Test on a separate instance before a production update. Do not rely on installing into a disposable running container.

## Updates

Back up the configuration and ensure a rollback wheel is available. Compare release notes with the Paperless version actually installed. Test a representative `.eml` and its attachment processing before promoting to production. Installing a new version does not automatically regenerate existing PDFs.

## Rollback

```bash
uv pip uninstall --python /opt/paperless/.venv/bin/python paperless-ngx-mail-header
```

After uninstalling, restart consumer, workers and web server as applicable and check that `get_parser_for_file("message/rfc822", ...)` selects the built-in parser. No database schema or storage-path changes are made by this package. Old PDFs remain as generated until an explicit reprocessing action.
