# Troubleshooting

**No header in HTML mail:** Check that the selected parser for `message/rfc822` is `Paperless-ngx Mail Header`, then inspect the email's MIME parts and the Paperless mail rule's PDF layout. Restart the services that load parser registry after package installation.

**No original HTML body:** Ensure the mail rule selects an HTML-containing layout. The plugin does not replace the mail rule or infer HTML that is absent.

**Missing logos/products:** Check Gotenberg's `--chromium-allow-list`, outbound firewall, DNS and remote image URLs. This is **not** necessarily a plugin failure. Review [privacy-security.md](privacy-security.md).

**Unwanted duplicate mail and attachment documents:** Check the native Paperless mail rule consumption scope and attachment filters. This plugin does not manage either.

**Import fails after an update:** Check exact Paperless and Python version, plugin selection log, traceback, then uninstall the plugin and restart the affected services to return to the native parser. Do not delete documents or disable OCR as a first response.

**Wrong timestamp:** Check the message's original RFC822 Date header and timestamp parsing. From 0.3.1 the plugin formats dates in Paperless's effective TIME_ZONE (`PAPERLESS_TIME_ZONE`, default UTC); it cannot correct an incorrect source Date header. Earlier versions always used Europe/Berlin. Restart Paperless services after changing configuration, and remember existing PDFs retain their generated timestamps.

**Old PDFs unchanged:** Installing this plugin affects future parsing only; reprocessing existing docs is a separate action with its own integrity/backup risks.
