# Security Policy

Checkpoint handles local project context and generated agent handoffs. Treat
security reports seriously, especially anything involving secret leakage,
unexpected file reads, unsafe writes, or generated handoffs that include private
credentials.

## Supported Versions

Checkpoint is pre-1.0. Security fixes target the latest commit on `main` until
formal release branches exist.

## Reporting A Vulnerability

Do not open a public issue for a vulnerability.

Use GitHub private vulnerability reporting for this repository. If that is not
available, open a minimal public issue that says only "security report needed"
and do not include exploit details, secrets, private URLs, or logs.

Useful report contents:

- Affected command or workflow
- Operating system and Python version
- Minimal reproduction steps
- What private data could be exposed or modified
- Whether the issue requires a malicious repo, malicious handoff, or normal use

## Security Boundaries

Expected behavior:

- Generated handoffs and continuation packs redact common secret patterns.
- Local event logs store metadata, not continuation pack contents.
- Project context files are plain Markdown and should be reviewed before commit.
- Future remote sync must be encrypted before upload.

Not yet in scope:

- Hosted sync
- Browser or IDE extensions
- Enterprise policy enforcement
- Sandboxed execution of arbitrary repository content

## Maintainer Response

For confirmed issues, maintainers should:

1. Acknowledge receipt.
2. Reproduce privately.
3. Patch on a private branch when needed.
4. Add regression coverage.
5. Publish a release note that describes impact without exposing secrets or
   exploit-ready detail.
