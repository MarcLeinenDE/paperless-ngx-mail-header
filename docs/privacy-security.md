# Privacy and security

## Scope of this plugin

The plugin uses parsed mail metadata already available to Paperless. It adds escaped text into a PDF header without new network calls or database fields. Do not confuse this with remote image fetching, which is handled by **Gotenberg/Chromium**.

## Remote images

An external image referenced by HTML can be requested while the email PDF is generated. This may reveal the conversion machine's public IP and the fact that the message was rendered; it may include tracking pixels. The original PDF should not need to fetch images again once rendering has completed.

Gotenberg `8.34` supports separate settings including `--chromium-disable-javascript=true` and `--chromium-deny-private-ips=true`. Confirm behavior on the exact deployed Gotenberg version. If you remove a restrictive `--chromium-allow-list`, private IP checks may then apply, but a broad explicit allow-list match can bypass IP-class checks: **do not blindly allow all HTTPS URLs while assuming the private-IP flag will still block internal destinations**.

See the upstream [configuration reference](https://gotenberg.dev/docs/configuration) and [outbound URL filtering guide](https://gotenberg.dev/docs/outbound-url-filtering) for the exact flags, defaults and allow-list precedence. The plugin does not change these settings.

Remote images may still be missing because of expired URLs, broken TLS, host blocking, cookie requirements or lazy-loading. Do not solve that by enabling JavaScript globally without a separate threat review.

## Confidential material

- Do not commit real `.eml`, invoice PDFs, customer IDs or private mail screenshots.
- Use generated example addresses and text in CI and documentation.
- Always verify security of forwarded emails and origin signatures separately from the rendered PDF.
