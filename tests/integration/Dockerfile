FROM ghcr.io/paperless-ngx/paperless-ngx:3.3.0
COPY dist/paperless_ngx_mail_header-0.2.0-py3-none-any.whl /tmp/
RUN uv pip install --system --no-deps /tmp/paperless_ngx_mail_header-0.2.0-py3-none-any.whl \
    && rm /tmp/paperless_ngx_mail_header-0.2.0-py3-none-any.whl
