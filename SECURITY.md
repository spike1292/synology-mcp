# Security Policy

## Supported versions

The latest released version receives security fixes. Please upgrade before
reporting an issue.

## Reporting a vulnerability

**Please do not open a public issue for security vulnerabilities.**

Instead, report privately via GitHub's
[private vulnerability reporting](https://github.com/rafalr100/synology-mcp/security/advisories/new)
(Security → Report a vulnerability). Include:

- a description of the issue and its impact,
- steps to reproduce, and
- affected version / environment.

You can expect an initial response within a few days.

## Scope & handling your data

This server connects to **your own NAS on your local network** and runs locally:

- Credentials are read from environment variables / a local `.env` file and are
  **never** committed, logged, or transmitted anywhere except to your NAS.
- HTTP request logging is suppressed so credentials and session ids do not reach
  stderr.
- Read-only fork: no tool changes NAS state. TLS certificates are verified by default.

## Hardening recommendations

- Use a **dedicated DSM account** with the minimum privileges you need rather
  than the main admin account.
- Keep the server on a trusted network; do not expose it to the internet.
- If your account uses 2FA, prefer the trusted-device token flow over storing an
  OTP.
