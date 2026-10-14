# Security

No persistent tokens, ATS credentials, LinkedIn cookies, or Gmail credentials are stored. GitHub Actions supplies a short-lived repository token, with write access scoped to report persistence. Pull-request tests have read-only permissions and no secrets.

External job content is parsed as data and escaped before presentation. The collector requires public HTTPS URLs, exact permitted hosts or official ATS-provided destination hosts, public DNS addresses, validated redirects, timeouts, limited retries, and response-size limits. DNS checks do not fully prevent DNS rebinding; use disposable hosted runners rather than a runner connected to private networks.

Do not commit resumes, application emails, candidate portal links, private notes, or credentials. A public repository exposes reports and any application exclusions committed to it. `.gitignore` is not a substitute for reviewing commits. Revoke leaked credentials immediately.

No applications or messages are sent to employers. Login, CAPTCHA, and access restrictions are not bypassed. Email delivery from this chat uses the connected mail service and requires user authorization; it is separate from the repository workflow.

For stricter supply-chain policies, pin official GitHub Actions to verified commit SHAs and review dependency updates. The current workflows use maintained major-version references.
