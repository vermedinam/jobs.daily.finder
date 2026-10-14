"""Conservative, dependency-free daily job collector. Remote content is data only."""
import argparse
import html
import ipaddress
import json
import re
import socket
import time
from datetime import datetime, date, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, urlencode, quote
from urllib.request import Request, build_opener, HTTPRedirectHandler
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo('America/Los_Angeles')
TITLES = ['Program Manager', 'Senior Program Manager', 'Technical Program Manager',
          'Senior Technical Program Manager', 'Delivery Manager', 'Producer', 'Senior Producer']


def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', str(value or '')))).strip()


def md(value):
    return html.escape(clean(value), quote=False).replace('|', '&#124;').replace('[', '&#91;').replace(']', '&#93;')


def canonical(url):
    p = urlsplit(url)
    # Preserve job-identifying query parameters; remove tracking only.
    from urllib.parse import parse_qsl
    query = urlencode([(k, v) for k, v in parse_qsl(p.query) if not k.lower().startswith('utm_') and k not in ('source', 'ref', 'trk')])
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip('/'), query, ''))


def title_ok(title):
    if re.search(r'\blead\b', title, re.I):
        return False
    text = clean(title).casefold()
    if re.search(r'\b(principal|staff|director|associate|executive|intern|vp)\b', text):
        return False
    text = re.sub(r'\bsr\.?\s+', 'senior ', text)
    return bool(re.search(r'\b(program manager|delivery manager|producer|tpm)\b', text))


def local_date(raw):
    if not isinstance(raw, str):
        raise ValueError('Missing publication date')
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', raw):
        return date.fromisoformat(raw)
    dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Timestamp has no timezone')
    return dt.astimezone(TZ).date()


def public_url(url, hosts):
    p = urlsplit(url)
    if p.scheme != 'https' or p.username or p.password or p.port not in (None, 443):
        raise ValueError('Only public HTTPS URLs are allowed')
    host = p.hostname or ''
    if host not in hosts:
        raise ValueError('Host is not explicitly allowlisted')
    for record in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(record[4][0]).is_global:
            raise ValueError('Private network address refused')


class SafeRedirect(HTTPRedirectHandler):
    def __init__(self, hosts):
        self.hosts = hosts
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_url(newurl, self.hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Client:
    def __init__(self, hosts):
        self.hosts = set(hosts)
        self.opener = build_opener(SafeRedirect(self.hosts))
    def get(self, url):
        public_url(url, self.hosts)
        for attempt in range(3):
            try:
                req = Request(url, headers={'User-Agent': 'jobs.daily.finder/1.0 (public job research)', 'Accept': 'application/json,text/html'})
                with self.opener.open(req, timeout=20) as res:
                    body = res.read(16_000_001)
                    if len(body) > 16_000_000:
                        raise ValueError('Response too large')
                    return body.decode('utf-8', errors='replace'), res.geturl()
            except Exception as exc:
                from urllib.error import HTTPError
                if isinstance(exc, HTTPError) and exc.code in (401, 403, 404, 410):
                    raise
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
    def json(self, url):
        return json.loads(self.get(url)[0])


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.buffer = ''
        self.items = []
    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('type', '').lower() == 'application/ld+json':
            self.active = True
            self.buffer = ''
    def handle_data(self, data):
        if self.active:
            self.buffer += data
    def handle_endtag(self, tag):
        if tag == 'script' and self.active:
            try:
                self.items.append(json.loads(self.buffer))
            except ValueError:
                pass
            self.active = False


def postings(node):
    if isinstance(node, list):
        for item in node:
            yield from postings(item)
    elif isinstance(node, dict):
        typ = node.get('@type', [])
        if typ == 'JobPosting' or isinstance(typ, list) and 'JobPosting' in typ:
            yield node
        if '@graph' in node:
            yield from postings(node['@graph'])


ALLOWED_COUNTRIES = {'us','usa','united states','united states of america','mx','mex','mexico','méxico',
    'ca','can','canada','br','brazil','brasil','ar','argentina','cl','chile','co','colombia','cr','costa rica',
    'uy','uruguay','pe','peru','perú','ec','ecuador','pa','panama','panamá','gt','guatemala','sv','el salvador',
    'hn','honduras','ni','nicaragua','bo','bolivia','py','paraguay','ve','venezuela','do','dominican republic',
    'república dominicana','pr','puerto rico','cu','cuba'}


def geography(location, countries=(), remote=False):
    countries = {str(c).casefold() for c in countries if c}
    if countries:
        return bool(countries & ALLOWED_COUNTRIES)
    allowed = r'united states|usa|mexico|méxico|canada|toronto|vancouver|montreal|montréal|ottawa|quebec|ontario|british columbia|brazil|brasil|argentina|chile|colombia|costa rica|uruguay|peru|perú|ecuador|panama|panamá|guatemala|el salvador|honduras|nicaragua|bolivia|paraguay|venezuela|dominican republic|puerto rico|latam|latin america|california|new york|texas|washington|massachusetts|illinois|florida|colorado|oregon|georgia|arizona|virginia|north carolina|new jersey|pennsylvania|utah|nevada|guadalajara|monterrey|san francisco|los angeles|san diego|san jose|santa monica|san mateo|mountain view|palo alto|sunnyvale|irvine|foster city|costa mesa|redwood city|buenos aires|bogotá|bogota|são paulo|sao paulo|medellin|medellín|santiago|lima'
    if re.search(r'\b(' + allowed + r')\b', location, re.I):
        return True
    if re.search(r'\b(united kingdom|uk|france|germany|india|australia|spain|japan|singapore|china|ireland|poland|netherlands|emea|europe|apac)\b', location, re.I):
        return False
    return bool(remote or re.search(r'\b(remote|remoto|worldwide|global)\b', location, re.I))


def california(job):
    return bool(re.search(r'\b(california|san francisco|los angeles|san diego|san jose|santa monica|san mateo|mountain view|palo alto|sunnyvale|irvine|foster city|costa mesa|redwood city)\b|,\s*CA\b', job['location'], re.I))


def schema_job(page, url, today):
    parser = Scripts()
    parser.feed(page)
    items = list(postings(parser.items))
    if len(items) != 1:
        return None  # Refuse job search/board pages and ambiguous structured data.
    item = items[0]
    if not title_ok(item.get('title', '')) or local_date(item.get('datePosted')) != today:
        return None
    expiry = item.get('validThrough')
    if expiry and local_date(expiry) < today:
        return None
    locs = item.get('jobLocation', [])
    locs = locs if isinstance(locs, list) else [locs]
    addresses = [x.get('address', {}) for x in locs if isinstance(x, dict)]
    locations = [', '.join(str(a.get(k, '')) for k in ('addressLocality', 'addressRegion', 'addressCountry') if a.get(k)) for a in addresses if isinstance(a, dict)]
    countries = [a.get('addressCountry') for a in addresses if isinstance(a, dict) and a.get('addressCountry')]
    remote = item.get('jobLocationType') == 'TELECOMMUTE'
    eligibility = item.get('applicantLocationRequirements', [])
    eligibility = eligibility if isinstance(eligibility, list) else [eligibility]
    required = [a.get('name', '') for a in eligibility if isinstance(a, dict)]
    if remote and required:
        countries = required
    location = '; '.join(locations + (['Remote' + (': ' + ', '.join(required) if required else ' (eligibility to confirm)')] if remote else []))
    if not geography(location, countries, remote):
        return None
    company = item.get('hiringOrganization', {}).get('name', '')
    if not company or not location:
        return None
    salary = item.get('baseSalary')
    return dict(id='url:' + canonical(url), company=clean(company), title=clean(item['title']),
                location=location, salary=clean(json.dumps(salary, ensure_ascii=False)) if salary else 'Not disclosed',
                official_url=url, posted=item['datePosted'], date_evidence='JobPosting.datePosted',
                evidence_url=url, description=clean(item.get('description')), linkedin_url='')


def work_mode(job, structured=None):
    text = clean(html.unescape(job.get('description','')))
    location = job.get('location','')
    if structured in ('Hybrid','Remote','OnSite'):
        return {'Hybrid':'Hybrid','Remote':'Remote','OnSite':'On-site'}[structured], 'Official workplaceType field: ' + structured
    # Explicit requirements take precedence over generic tags or event/onboarding references.
    patterns = [
        ('Hybrid', r'[^.]{0,100}(?:this role|this position|the role|position|role).{0,80}(?:hybrid|in.person collaboration 1.2 times/week)[^.]{0,180}'),
        ('Remote', r'[^.]{0,100}(?:this position|this role|the role).{0,80}(?:remote eligible|fully remote|100% remote|remote position)[^.]{0,180}'),
        ('On-site', r'[^.]{0,70}(?:required on.site|required to be performed full.time from|this (?:position|role) (?:is|will be|must be) (?:strictly |fully |100% )?(?:on.site|onsite|in.office))[^.]{0,180}')
    ]
    for label, pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return label, match.group(0).strip()
    if re.search(r'on.site presence and requirements may change', text, re.I):
        return 'Not specified', 'On-site attendance depends on client needs; a fixed work arrangement or frequency is not specified.'
    if re.search(r'\bremote\b', location, re.I):
        return 'Remote available', 'The official location includes remote work; confirm geographic restrictions and other work arrangements with the employer.'
    return 'Not specified', 'The reviewed official source does not confirm the work arrangement for this role.'


FOCUS_PATTERNS = {
    'Agile': r'\b(?:agile|agilidad|scrum|kanban|sprints?)\b',
    'OKRs': r'\b(?:okrs?|objectives and key results|objetivos y resultados clave)\b',
    'Operations': r'\b(?:operations|operaciones|operational excellence|operational readiness|operating model|process improvement|continuous improvement|excelencia operativa|mejora continua)\b',
    'ISO 27001': r'\biso\s*(?:/\s*iec\s*)?[- ]?27001\b'
}


def focus_matches(job, profile):
    text = clean(html.unescape(job.get('title','') + '. ' + job.get('description','')))
    found = []
    evidence = {}
    for name in profile.get('focus_categories', []):
        pattern = FOCUS_PATTERNS.get(name)
        match = re.search(pattern, text, re.I) if pattern else None
        if match:
            found.append(name)
            evidence[name] = text[max(0,match.start()-60):min(len(text),match.end()+100)]
    return found, evidence


def score(job, profile):
    # This is an explainable relevance heuristic, not a hiring probability.
    if profile.get('focus_categories'):
        matched, _ = focus_matches(job, profile)
        return min(100, 40 + 15 * len(matched)), matched
    terms = profile.get('skills', [])
    text = job['description'].casefold()
    matched = [s for s in terms if re.search(r'(?<!\w)' + re.escape(s.casefold()) + r'(?!\w)', text)]
    value = 60 + (10 if job['title'].casefold().startswith('senior ') else 0)
    value += round(30 * len(matched) / max(1, len(terms)))
    return min(100, value), matched


def collect(config, client, today, metrics):
    jobs = []
    for source in config['boards']:
        kind, slug, company = source['type'], quote(source['slug'], safe=''), source['company']
        try:
            if kind == 'greenhouse':
                endpoint = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs'
                entries = client.json(endpoint)['jobs']
            elif kind == 'ashby':
                endpoint = f'https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true'
                entries = client.json(endpoint)['jobs']
            elif kind == 'amazon':
                endpoint = 'https://www.amazon.jobs/en/search.json'
                entries = []
                for query in ('program manager', 'delivery manager', 'producer'):
                    for offset in range(0, 5000, 100):
                        data = client.json(endpoint + '?' + urlencode({'base_query':query, 'sort':'recent', 'offset':offset, 'result_limit':100}))
                        entries.extend(data.get('jobs', []))
                        if offset + 100 >= data.get('hits', 0):
                            break
                    else:
                        metrics['errors'].append(f'Amazon: pagination capped for {query}')
            elif kind == 'smartrecruiters':
                endpoint = f'https://api.smartrecruiters.com/v1/companies/{slug}/postings'
                entries = []
                for offset in range(0, 20000, 100):
                    data = client.json(endpoint + '?' + urlencode({'limit':100,'offset':offset}))
                    entries.extend(data.get('content', []))
                    if offset + 100 >= data.get('totalFound', 0):
                        break
                else:
                    metrics['errors'].append(f'{company}: pagination capped at 20,000 jobs')
            else:
                raise ValueError('Unsupported board type')
            metrics['sources_ok'] += 1
        except Exception as exc:
            metrics['errors'].append(f'{company}: {type(exc).__name__}')
            continue
        for entry in entries:
            metrics['reviewed'] += 1
            if not title_ok(entry.get('title', entry.get('name', ''))):
                continue
            try:
                if kind == 'greenhouse':
                    detail_url = endpoint + '/' + str(entry['id']) + '?pay_transparency=true'
                    detail = client.json(detail_url)
                    posted = detail.get('first_published')
                    if local_date(posted) != today:
                        continue
                    loc = detail.get('location', {}).get('name', '')
                    countries = [o.get('location') for o in entry.get('offices', []) if str(o.get('location','')).casefold() in ALLOWED_COUNTRIES]
                    if not geography(loc, countries):
                        continue
                    url = detail.get('absolute_url', entry['absolute_url'])
                    client.hosts.add(urlsplit(url).hostname)  # official destination supplied by the ATS API
                    page, final_url = client.get(url)
                    # API listing + detail identify the live job; require same job ID in destination URL/page.
                    if str(entry['id']) not in final_url and str(entry['id']) not in page:
                        raise ValueError('Cannot verify destination job identity')
                    if re.search(r'job (?:is no longer|has been filled)|position (?:is no longer|has been filled)', clean(page), re.I):
                        continue
                    ranges = detail.get('pay_input_ranges', [])
                    salary = '; '.join(f"{r['currency_type']} {r['min_cents']/100:,.0f}-{r['max_cents']/100:,.0f} ({r.get('title', 'interval not specified')})" for r in ranges if all(r.get(k) is not None for k in ('currency_type', 'min_cents', 'max_cents'))) or 'Not disclosed'
                    jobs.append(dict(id=f'greenhouse:{source["slug"]}:{entry["id"]}', company=detail.get('company_name') or company,
                                     title=detail['title'], location=loc, salary=salary, official_url=final_url,
                                     posted=posted, date_evidence='Greenhouse.first_published', evidence_url=detail_url,
                                     description=clean(detail.get('content')), linkedin_url=''))
                elif kind == 'amazon':
                    posted = entry.get('posted_date')
                    parsed = datetime.strptime(posted, '%B %d, %Y').date()
                    if parsed != today:
                        continue
                    loc = entry.get('location', '')
                    if not geography(loc, [entry.get('country_code')]):
                        continue
                    url = 'https://www.amazon.jobs' + entry['job_path']
                    page, final_url = client.get(url)
                    if str(entry['id_icims']) not in final_url and str(entry['id_icims']) not in page:
                        raise ValueError('Cannot verify Amazon destination identity')
                    if re.search(r'job (?:is no longer|has been filled)|position (?:is no longer|has been filled)', clean(page), re.I):
                        continue
                    description = clean(entry.get('description','') + ' ' + entry.get('basic_qualifications','') + ' ' + entry.get('preferred_qualifications',''))
                    pay = re.findall(r'[A-Z]{3}, [^<>\n]+? - [0-9][0-9,]*\.[0-9]{2} - [0-9][0-9,]*\.[0-9]{2} [A-Z]{3} (?:annually|hourly)', html.unescape(entry.get('preferred_qualifications','')))
                    jobs.append(dict(id='amazon:' + str(entry['id_icims']), company='Amazon', title=entry['title'],
                        location=loc, salary='; '.join(pay) or 'Not disclosed', official_url=final_url,
                        posted=posted, date_evidence='Amazon Jobs.posted_date (declared date without timezone)',
                        evidence_url=endpoint + '?' + urlencode({'base_query':entry['id_icims']}), description=description, linkedin_url=''))
                elif kind == 'smartrecruiters':
                    posted = entry.get('releasedDate')
                    if local_date(posted) != today:
                        continue
                    detail_url = endpoint + '/' + str(entry['id'])
                    detail = client.json(detail_url)
                    posted = detail.get('releasedDate', posted)
                    if local_date(posted) != today:
                        continue
                    address = detail.get('location', {})
                    loc = ', '.join(str(address.get(k,'')) for k in ('city','region','country') if address.get(k))
                    if address.get('remote'): loc += ' (Remote)'
                    if not geography(loc, [address.get('country')], address.get('remote',False)):
                        continue
                    url = detail.get('postingUrl') or detail.get('applyUrl')
                    if not url: raise ValueError('No direct official URL')
                    client.hosts.add(urlsplit(url).hostname)
                    page, final_url = client.get(url)
                    if str(entry['id']) not in final_url and str(entry['id']) not in page:
                        raise ValueError('Cannot verify destination identity')
                    sections = detail.get('jobAd',{}).get('sections',{})
                    jobs.append(dict(id=f'smartrecruiters:{source["slug"]}:{entry["id"]}', company=detail.get('company',{}).get('name') or company,
                        title=detail['name'], location=loc, salary='Not disclosed', official_url=final_url, posted=posted,
                        date_evidence='SmartRecruiters.releasedDate (release; may be a repost)', evidence_url=detail_url,
                        description=clean(' '.join(x.get('text','') for x in sections.values())), linkedin_url=''))
                else:
                    if not entry.get('isListed'):
                        continue
                    if entry.get('publishedAt') and local_date(entry['publishedAt']) < today:
                        continue
                    # publishedAt means LAST publication: never use it as proof of original posting.
                    page, url = client.get(entry['jobUrl'])
                    job = schema_job(page, url, today)
                    if job:
                        job['id'] = 'ashby:' + source['slug'] + ':' + urlsplit(url).path.rstrip('/').split('/')[-1]
                        job['salary'] = entry.get('compensation', {}).get('scrapeableCompensationSalarySummary') or job['salary']
                        job['work_mode'], job['work_mode_evidence'] = work_mode(job, entry.get('workplaceType'))
                        jobs.append(job)
            except Exception as exc:
                metrics['unverified'] += 1
                metrics['errors'].append(f'{company} / {entry.get("id", entry.get("title"))}: {type(exc).__name__}')
    return jobs


def linkedin(config, client, today, jobs, metrics):
    if not config.get('linkedin_public', True):
        metrics['linkedin'] = 'Disabled in configuration'
        return
    accessible = 0
    for location in ('California, United States', 'United States', 'Canada', 'Mexico', 'Latin America'):
        for title in TITLES:
            query = urlencode({'keywords': title, 'location': location, 'f_TPR': 'r86400' if today == datetime.now(TZ).date() else 'r604800', 'start': 0})
            try:
                page, _ = client.get('https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?' + query)
                accessible += 1
            except Exception as exc:
                metrics['linkedin'] = f'Public access limited ({type(exc).__name__}); no bypass or login attempted'
                return
            for card in re.findall(r'<li\b[^>]*>(.*?)</li>', page, re.S):
                t = re.search(r'<h3\b[^>]*>(.*?)</h3>', card, re.S)
                c = re.search(r'<h4\b[^>]*>(.*?)</h4>', card, re.S)
                link = re.search(r'https://(?:www\.)?linkedin\.com/jobs/view/[^"\s<>]+', card)
                if not (t and c and link) or not title_ok(clean(t[1])):
                    continue
                url = canonical(html.unescape(link[0]))
                metrics['linkedin_candidates'] += 1
                # Never trust LinkedIn relative dates. Match official verified jobs first.
                for job in jobs:
                    if clean(t[1]).casefold() == job['title'].casefold() and clean(c[1]).casefold() == job['company'].casefold():
                        job['linkedin_url'] = url
                try:
                    detail, _ = client.get(url)
                    # Official outbound links only from configured trusted domains.
                    for target in re.findall(r'href=["\'](https://[^"\']+)', detail):
                        target = html.unescape(target)
                        if urlsplit(target).hostname not in config['official_hosts']:
                            continue
                        official, final = client.get(target)
                        job = schema_job(official, final, today)
                        if job and job['title'].casefold() == clean(t[1]).casefold() and job['company'].casefold() == clean(c[1]).casefold():
                            job['linkedin_url'] = url
                            jobs.append(job)
                except Exception:
                    metrics['unverified'] += 1
            time.sleep(0.3)
    metrics['linkedin'] = f'Public access available: {accessible} searches; publication dates verified only against official sources'


def load(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)


def select(jobs, state, applied, today, metrics, profile):
    unique = {}
    blocked_ids = {x.get('id') for x in applied}
    blocked_urls = {canonical(x['official_url']) for x in applied if x.get('official_url')}
    for job in jobs:
        url = canonical(job['official_url'])
        topics, evidence = focus_matches(job, profile)
        if profile.get('require_focus') and not topics:
            metrics['focus_excluded'] = metrics.get('focus_excluded', 0) + 1
            continue
        job['focus_matches'], job['focus_evidence'] = topics, evidence
        if job['id'] in blocked_ids or url in blocked_urls:
            metrics['applied_excluded'] += 1
            continue
        previous = state['seen'].get(job['id']) or next((v for v in state['seen'].values() if v['url'] == url), None)
        if previous and previous['first_seen'] != today.isoformat():
            metrics['seen_excluded'] += 1
            continue
        state['seen'].setdefault(job['id'], {'url': url, 'first_seen': today.isoformat(), 'last_seen': today.isoformat()})
        state['seen'][job['id']]['last_seen'] = today.isoformat()
        job.setdefault('work_mode', work_mode(job)[0])
        job.setdefault('work_mode_evidence', work_mode(job)[1])
        job['match'], job['matched_skills'] = score(job, profile)
        if url in unique:
            if job.get('linkedin_url'):
                unique[url]['linkedin_url'] = job['linkedin_url']
        else:
            unique[url] = job
    return sorted(unique.values(), key=lambda j: (-j['match'], not california(j), j['company'], j['title']))[:20]


ENCOURAGEMENT = "Your worth is not measured by an inbox. One thoughtful application at a time is enough for today."


def report(today, jobs, metrics, now):
    lines = [f'# Daily Job Report: {today}', '', f'> {ENCOURAGEMENT}', '',
        f'Publication day: {today}. Verified at: {now.isoformat()} (America/Los_Angeles).', '',
        'Up to 20 verified listings from the requested publication day. Coverage is limited to accessible sources.', '',
        f"Reviewed: {metrics['reviewed']} | Recommended: {len(jobs)} | Applied excluded: {metrics['applied_excluded']} | Previously seen: {metrics['seen_excluded']} | Unverified: {metrics['unverified']} | Outside topic focus: {metrics.get('focus_excluded',0)}", '',
        f"Accessible sources: {metrics['sources_ok']} | LinkedIn candidates: {metrics['linkedin_candidates']}", '',
        f"LinkedIn: {md(metrics['linkedin'])}", '', '## Top 5', '']
    for j in jobs[:5]:
        lines.append(f"- **{j['match']}% estimated topic match** | {md(j['company'])} | [{md(j['title'])}](<{j['official_url']}>) | {md(j.get('work_mode','Not specified'))}")
    if not jobs: lines.append('No verified listings met all filters in the accessible sources.')
    lines += ['', '## Verified jobs', '', '| Estimated match | Company / role | Location | Work arrangement | Published salary | Official publication date | Apply | LinkedIn |', '|---|---|---|---|---|---|---|---|']
    for j in jobs:
        li = f"[LinkedIn](<{j['linkedin_url']}>)" if j.get('linkedin_url') else 'Not available'
        lines.append(f"| {j['match']}% | {md(j['company'])} / {md(j['title'])} | {md(j['location'])} | {md(j.get('work_mode','Not specified'))} | {md(j['salary'])} | {md(j['posted'])} | [Apply](<{j['official_url']}>) | {li} |")
    lines += ['', '## Evidence and fit', '', 'Topic match is a heuristic, not a hiring probability or verified assessment of experience. With topic focus enabled: 40 base points plus 15 per matched theme (Agile, OKRs, Operations, ISO 27001), capped at 100. At least one theme is required. Results are ordered by match; California breaks ties.', '']
    for j in jobs:
        lines += [f"### {md(j['company'])}: {md(j['title'])}", '', f"- Job ID: {md(j['id'])}",
            '- Application status: Not recorded as applied',
            f"- Work arrangement: {md(j.get('work_mode','Not specified'))}. {md(j.get('work_mode_evidence',''))}",
            f"- Publication date: {md(j['posted'])}. Zoned timestamps are evaluated in California time.",
            f"- Date evidence: [{md(j['date_evidence'])}](<{j['evidence_url']}>)",
            f"- Relevant themes: {md(', '.join(j.get('focus_matches',j.get('matched_skills',[]))) or 'None recorded')}.",
            *[f"- Theme evidence: the official title or description mentions {md(t)}." for t in j.get('focus_evidence',{})], '']
    lines += ['## Coverage and source issues', '', 'The daily 5 pm run cannot include listings published after it begins. Historical searches include postings still accessible when checked. First-seen dates are never substituted for publication dates. SmartRecruiters release dates may refer to reposts. Work arrangements are not inferred from a city or an onboarding event.']
    lines.extend('- '+md(e) for e in metrics['errors'])
    return ('\n'.join(lines)+'\n').replace('—','-').replace('–','-')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['run', 'applied'])
    parser.add_argument('--id')
    parser.add_argument('--url')
    parser.add_argument('--date', help='Publication day in California, YYYY-MM-DD; default today')
    args = parser.parse_args()
    if args.command == 'applied':
        if not args.id and not args.url:
            parser.error('Supply --id and/or --url from the report')
        entries = load(ROOT / 'data/applied.json', [])
        entries.append({'id': args.id, 'official_url': args.url, 'status': 'Applied'})
        save(ROOT / 'data/applied.json', entries)
        return
    config = load(ROOT / 'config/sources.json')
    profile = load(ROOT / 'config/profile.json')
    now = datetime.now(TZ)
    today = date.fromisoformat(args.date) if args.date else now.date()
    if today > now.date():
        parser.error('Cannot search future publication dates')
    historical = today != now.date()
    metrics = dict(reviewed=0, sources_ok=0, unverified=0, applied_excluded=0, seen_excluded=0, linkedin_candidates=0, linkedin='Not run', errors=[])
    client = Client(config['official_hosts'] + ['boards-api.greenhouse.io', 'api.ashbyhq.com', 'www.linkedin.com', 'linkedin.com'])
    from concurrent.futures import ThreadPoolExecutor
    def collect_one(source):
        stats = dict(reviewed=0, sources_ok=0, unverified=0, errors=[])
        worker = Client(client.hosts)
        result = collect({'boards':[source]}, worker, today, stats)
        return result, stats
    jobs = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for result, stats in pool.map(collect_one, config['boards']):
            jobs.extend(result)
            for key in ('reviewed','sources_ok','unverified'):
                metrics[key] += stats[key]
            metrics['errors'].extend(stats['errors'])
    linkedin(config, client, today, jobs, metrics)
    if not metrics['sources_ok']:
        raise SystemExit('No official board was accessible; refusing to overwrite the dashboard with a misleading empty report')
    state = {'seen': {}} if historical else load(ROOT / 'data/state.json', {'seen': {}})
    jobs = select(jobs, state, load(ROOT / 'data/applied.json', []), today, metrics, profile)
    text = report(today, jobs, metrics, now)
    if historical:
        text += '\nHistorical search: includes postings from that day still accessible now. Closed historical postings cannot be reconstructed. The current dashboard and seen history are preserved. Recorded applications remain excluded.\n'
    directory = ROOT / 'reports'
    directory.mkdir(exist_ok=True)
    (directory / f'{today}.md').write_text(text)
    save(directory / f'{today}.json', {'date': today.isoformat(), 'verified_at': now.isoformat(), 'metrics': metrics, 'jobs': jobs})
    if historical:
        print(f'{today}: {len(jobs)} verified historical jobs, {len(metrics["errors"])} source warnings')
        return
    readme = (ROOT / 'README.md').read_text()
    start, end = '<!-- DASHBOARD:START -->', '<!-- DASHBOARD:END -->'
    dashboard = text.replace(f'# Daily Job Report: {today}', f'## Dashboard: {today}').replace('](<reports/', '](<')
    # Dashboard report evidence links are absolute, so no link rewriting is needed.
    readme = readme.split(start)[0] + start + '\n\n' + dashboard + '\n' + end + readme.split(end)[1]
    (ROOT / 'README.md').write_text(readme)
    save(ROOT / 'data/state.json', state)
    print(f'{today}: {len(jobs)} verified jobs, {len(metrics["errors"])} source warnings')


if __name__ == '__main__':
    main()


