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