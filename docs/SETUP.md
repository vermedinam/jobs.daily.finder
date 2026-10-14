# Setup

Python 3.9 or newer with IANA timezone data is required. GitHub Actions uses Python 3.12. No third-party Python packages or ATS credentials are required.

1. Enable GitHub Actions on the repository's default branch.
2. The daily workflow requests `contents: write` only to persist reports and seen state. Protected branches may require an approved PR-based persistence mechanism.
3. Review `config/sources.json` and `config/profile.json`. Board identifiers can change; inaccessible sources are reported.
4. Import previously submitted applications into `data/applied.json` using official job IDs and/or direct URLs. Any entry in this file is excluded regardless of its status label. Remove an entry to undo an exclusion.
5. Open Actions, Daily job finder, Run workflow. Leave `date` blank for the current California day, or enter a publication date in YYYY-MM-DD format for a historical search.
6. Review the report, evidence, source issues, and verification timestamp. Scheduled workflows can be delayed; public repositories may have schedules disabled after prolonged inactivity.

The schedule is `0 17 * * *` with timezone `America/Los_Angeles`. A run does not include jobs posted after it begins. Historical searches leave the latest dashboard and seen state intact.

Example exclusion, using a fictional job:

```json
[{"id":"greenhouse:company:12345","official_url":"https://job-boards.greenhouse.io/company/jobs/12345","status":"Applied"}]
```

Use a private repository if application history should remain confidential. Gmail application confirmations are not automatically available to the GitHub workflow. This chat can cross-check them before sending a report, but that does not automatically populate the repository's exclusion file.

Emails are sent only through an authorized connected mail account when requested in chat. Do not place Gmail passwords or OAuth credentials in the repository.
