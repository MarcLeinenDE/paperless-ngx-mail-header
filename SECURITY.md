# Security

Report suspected security vulnerabilities through GitHub's [private vulnerability reporting form](https://github.com/MarcLeinenDE/paperless-ngx-mail-header/security/advisories/new). Provide a fully synthetic reproducer and only the diagnostics needed to explain the problem. Keep real email headers, authentication material, private URLs, invoices and document contents out of reports and public issues.

CodeQL analyzes Python and GitHub Actions. Dependabot provides dependency alerts and security-update pull requests; scheduled version-update PRs cover GitHub Actions and Python development tooling. Workflow actions are pinned to verified upstream commit SHAs. These checks support review and do not establish compatibility with every Paperless release or deploy updates to a production installation.

The plugin must not fetch external URLs itself. HTTP(S) loads performed by Gotenberg are separate from plugin execution. Keep JavaScript disabled for untrusted HTML and restrict private-network access according to the deployment's threat model.

Never run integration tests against a user's production inbox without permission. See [docs/privacy-security.md](docs/privacy-security.md).
