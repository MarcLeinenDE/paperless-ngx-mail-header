FROM ghcr.io/paperless-ngx/paperless-ngx:3.3.0
COPY dist/*.whl /tmp/mail-header-wheels/
RUN uv pip install --system --no-deps /tmp/mail-header-wheels/*.whl \
    && rm /tmp/mail-header-wheels/*.whl
