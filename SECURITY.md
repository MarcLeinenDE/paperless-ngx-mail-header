# Security

Do not report security issues by publishing real email headers, authentication material, private URLs, invoices or document contents. Use GitHub's private vulnerability-reporting feature if it becomes enabled in the repository; otherwise contact the maintainer privately using a channel listed on their GitHub profile.

The plugin must not fetch external URLs itself. HTTP(S) loads performed by Gotenberg are separate from plugin execution. Keep JavaScript disabled for untrusted HTML and restrict private-network access according to the deployment's threat model.

Never run integration tests against a user's production inbox without permission. See [docs/privacy-security.md](docs/privacy-security.md).
