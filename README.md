# jobs.daily.finder

> Your worth is not measured by an inbox. One thoughtful application at a time is enough for today.

Daily job discovery at **5 pm America/Los_Angeles**, with automatic daylight-saving adjustment. GitHub may delay scheduled runs.

Focus: **Agile, OKRs, Operations, and ISO 27001**. A listing must mention at least one theme in its official title or description. Target roles: Program Manager, Senior Program Manager, Technical Program Manager, Senior Technical Program Manager, Delivery Manager, Producer, and Senior Producer, including specialty modifiers and Sr./TPM abbreviations. Lead, Staff, Principal, Director, Associate, Executive, Intern, and VP titles are excluded.

Search area: USA, Canada, Mexico, Spain, LATAM, and eligible remote roles. Results are sorted by estimated topic match; California breaks ties. Up to 30 results from the exact requested publication day. Dates and listings are never invented to fill the quota.

<!-- DASHBOARD:START -->

## Dashboard

The next successful current-day run will refresh this dashboard. See [daily reports](reports/) for completed searches.

<!-- DASHBOARD:END -->

## What each listing includes

Official direct application URL, verified publication date and evidence, location, work arrangement, published salary when available, estimated topic match, relevant themes, and LinkedIn link when accessible. Work arrangements are labeled Remote, Hybrid, On-site, Remote available, or Not specified; a city alone is not evidence of office attendance.

Topic match = 40 base points plus 15 per matched theme, capped at 100. It is an explainable relevance heuristic, not a hiring probability, a certification claim, or a verified evaluation of your experience.

## Run and configure

```sh
python3 -m unittest discover -s tests -v
python3 -m jobfinder.bot run
python3 -m jobfinder.bot run --date 2026-10-13
python3 -m jobfinder.bot applied --id 'greenhouse:company:12345' --url 'https://job-boards.greenhouse.io/company/jobs/12345'
```

[Setup](docs/SETUP.md) | [Verification and coverage](docs/VERIFICATION.md) | [Security](SECURITY.md)

Sources are configured in `config/sources.json`; preferences in `config/profile.json`. Application exclusions are stored in `data/applied.json`; seen listings in `data/state.json`. The repository does not have direct access to Gmail and does not send emails automatically. Email delivery and inbox checks in this chat are separate actions. Import applications into the exclusion list to prevent repeat recommendations from scheduled runs. Do not put private emails or personal notes in a public repository.

Historical searches preserve the current dashboard and seen history. They verify postings still accessible now and cannot reconstruct closed historical listings. A run with no accessible official boards fails and preserves the prior report instead of presenting a misleading empty result.
\n## Mexico and Spain coverage\n\nThe result target is 30. Up to five eligible Mexico listings and five eligible Spain listings are retained before filling the remaining slots by topic match, so these regions are not crowded out by US listings. The final display remains sorted by descending match. The report shows the verified candidate count for each region; a zero means none met all filters in the consulted sources, not that the country has no openings. Publication dates are never broadened without the user requesting it.\n