ARG PAPERLESS_VERSION=3.3.0
FROM ghcr.io/paperless-ngx/paperless-ngx:${PAPERLESS_VERSION}
COPY dist/*.whl /tmp/mail-header-wheels/
RUN uv pip install --system --no-deps /tmp/mail-header-wheels/*.whl \
    && rm /tmp/mail-header-wheels/*.whl
