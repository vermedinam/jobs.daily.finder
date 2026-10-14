# Verification and coverage

Publication timestamps with offsets are evaluated in America/Los_Angeles. A date without a time is kept as declared by the official source. Relative dates, missing dates, first-seen dates, and modification timestamps are not publication evidence.

- Greenhouse: uses the official detail endpoint's `first_published`, never `updated_at`. Verifies the direct destination and job identity. Salary comes from published pay ranges.
- Ashby: discovers listed jobs, then requires `JobPosting.datePosted` on the official page. `publishedAt` means last publication and is not treated as proof of original publication. Explicit `workplaceType` is used for work arrangement.
- SmartRecruiters: paginates public listings, checks detail, and uses `releasedDate`. This is a release date and may represent a repost; that limitation is labeled. Verifies direct URL and job identity.
- Amazon Jobs: uses the employer's literal `posted_date`, not relative `updated_time`. Verifies the official direct job page and ID. Published salary ranges are preserved.
- LinkedIn: attempts public searches in California, USA, Canada, Mexico, and LATAM. Relative date filters are discovery only. A result requires independent official publication evidence. Authentication, CAPTCHAs, and access blocks are not bypassed. Coverage is limited to accessible public results.

A successful HTTP response does not prove a job is still accepting applications. The collector checks identity and explicit closure signals; some closure formats may remain undetected. Historical runs can only verify postings still accessible when checked.

## Relevance and ranking

At least one requested theme must occur in the official title or description: Agile (including Scrum, Kanban, and sprints), OKRs (including Objectives and Key Results), Operations, or ISO 27001/ISO/IEC 27001. Matching is deterministic and keyword-based; context still requires review. A generic mention does not establish professional fit or certification requirements.

Topic match = 40 + 15 per matched theme, capped at 100. Sort order is descending topic match, with California as a tie-breaker. Earlier reports preserve the scoring method under which they were created unless explicitly regenerated.

## Work arrangement

Use explicit official workplace fields or role-specific wording. Hybrid requirements take precedence over generic tags when a posting describes both. A one-time office onboarding, an in-person interview, or on-site event work is not treated as proof of a permanent on-site role. Missing or ambiguous arrangements are labeled Not specified.

## Data and safety

Only public HTTPS destinations are accepted. Official direct URLs supplied by ATS APIs may add their exact host for that query; private IPs and unauthorized redirects are refused. Source text is data, never executable instructions. Original employer names and source text may retain their original language in raw JSON; generated reports, explanations, and emails are English.

[Greenhouse documentation](https://docs.greenhouse.io/job-board.html) | [Ashby documentation](https://developers.ashbyhq.com/docs/public-job-posting-api) | [SmartRecruiters documentation](https://developers.smartrecruiters.com/docs/endpoints) | [GitHub timezone support](https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates/)
\n## Mexico and Spain coverage\n\nThe result target is 30. Up to five eligible Mexico listings and five eligible Spain listings are retained before filling the remaining slots by topic match, so these regions are not crowded out by US listings. The final display remains sorted by descending match. The report shows the verified candidate count for each region; a zero means none met all filters in the consulted sources, not that the country has no openings. Publication dates are never broadened without the user requesting it.\n
## Professional associations and specialist job boards

Discovery includes Prospanica, HOPE (Hispanas Organized for Political Equality), Lean In Latinas, Built In San Francisco, Hitmarker, Welcome to the Jungle, and Biocom Career Hub. WelbeHealth official careers and the confirmed Greenhouse boards for WelbeHealth and CHAOS Industries are also searched. Each report records accessible seed pages, candidate pages, verified discoveries, and issues for these sources.

The collector respects robots.txt and uses public HTML only. A configured source is not a guarantee of access or full coverage: member-only, dynamically loaded, blocked, and unavailable pages are reported. Third-party board dates and relative dates cannot qualify a vacancy. Candidates must resolve to a configured official employer or ATS host with a single JobPosting and an exact requested datePosted. Unknown employer hosts require verification and configuration before being fetched. Existing applied exclusions and topic filters apply after discovery. No assumption is made that a non-Amazon employer is easier to enter.

## Search scope: categories, not a closed list

User-supplied websites are examples of source categories, not an exclusive whitelist. The discovery catalog covers Latino and professional associations; women and inclusive career networks; regional technology and startups; games and entertainment; life sciences; remote and international boards; and official company careers. California remains a priority, with USA, Mexico, Canada, Latin America, Spain, and eligible remote roles in scope. The catalog currently contains 31 discovery entries in addition to the existing ATS company catalog.

The catalog is a starting network, not a claim to search every site on the internet. Each accessible board can introduce new employers: the collector recognizes exact Greenhouse, Ashby, and SmartRecruiters destinations, verifies their public ATS endpoint, searches qualifying roles, and retains successful boards in data/discovered.sources.json for future runs. Up to 30 new employer boards are verified per run; cached boards are included in subsequent runs. Unsupported employer platforms and additional third-party boards require further source research or adapters. Access and partial-coverage limitations stay visible in each report. Adding a source does not prove that it is accessible or that it produced a qualifying vacancy.

October 13 historical results are not expanded to other dates. The 30-result target, official date verification, topic filter, match ordering, table format, and recorded-application exclusions remain in effect.
